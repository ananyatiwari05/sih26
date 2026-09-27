"""
Module D: Confidence & Anomaly Classification Engine.

Rules run in priority order (a parcel/structure earns exactly one class — the
first rule that fires wins, mirroring how the spec numbers them 1..6):

  1. RED    GHOST_STRUCTURE    nDSM structure present, no cadastral/revenue match
  2. ORANGE PHANTOM_RECORD     cadastral/revenue record present, no nDSM structure
  3. YELLOW BOUNDARY_DRIFT     matched but polygons offset 1-3m
  4. BLUE   ATTRIBUTE_MISMATCH geometries match, revenue attrs conflict
  5. PURPLE DUPLICATE_IDENTITY >1 record ID mapped to the same physical parcel
  6. BLACK  TEMPORAL_GHOST     appears/disappears across survey epochs
  -         VERIFIED           none of the above -> clean parcel
"""
from __future__ import annotations
from dataclasses import dataclass, field

from app.config import settings
from app.schemas.anomaly import AnomalyClass
from app.pipeline.spatial_matching import MatchResult
from app.utils.geometry_utils import haversine_m, centroid_of


@dataclass
class ClassificationInput:
    parcel_id: str
    match: MatchResult
    parcel_attrs: dict = field(default_factory=dict)
    structure_attrs: dict = field(default_factory=dict)
    parcel_coords: list[list[float]] | None = None
    structure_coords: list[list[float]] | None = None
    duplicate_record_ids: list[str] = field(default_factory=list)   # >1 => PURPLE
    epoch_presence: dict[str, bool] = field(default_factory=dict)   # {"2021": True, "2023": False, ...}
    attribute_conflict_fields: list[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    parcel_id: str
    anomaly_class: AnomalyClass
    confidence: float
    rationale: str
    drift_margin_m: float | None = None


def _boundary_drift_margin_m(parcel_coords, structure_coords) -> float:
    return haversine_m(centroid_of(parcel_coords), centroid_of(structure_coords))


def is_temporal_ghost(epoch_presence: dict[str, bool]) -> bool:
    """True if the structure toggles present/absent across >=1 epoch transition
    (appears, disappears, then reappears -> at least 2 flips in the sequence)."""
    values = [v for _, v in sorted(epoch_presence.items())]
    flips = sum(1 for i in range(1, len(values)) if values[i] != values[i - 1])
    return flips >= 2


def classify(inp: ClassificationInput) -> ClassificationResult:
    has_structure = inp.match.structure_id is not None
    has_record = bool(inp.parcel_attrs)

    # 6. TEMPORAL_GHOST — checked first: cross-epoch flicker overrides a single-epoch read
    if inp.epoch_presence and is_temporal_ghost(inp.epoch_presence):
        return ClassificationResult(
            parcel_id=inp.parcel_id,
            anomaly_class=AnomalyClass.TEMPORAL_GHOST,
            confidence=90.0,
            rationale=(
                f"Structure toggles across survey epochs "
                f"({', '.join(f'{y}:{'present' if p else 'absent'}' for y, p in sorted(inp.epoch_presence.items()))}) "
                "— inconsistent with a stable physical structure."
            ),
        )

    # 5. DUPLICATE_IDENTITY
    if len(inp.duplicate_record_ids) > 1:
        return ClassificationResult(
            parcel_id=inp.parcel_id,
            anomaly_class=AnomalyClass.DUPLICATE_IDENTITY,
            confidence=93.0,
            rationale=(
                f"{len(inp.duplicate_record_ids)} conflicting record IDs "
                f"({', '.join(inp.duplicate_record_ids)}) map to the same physical parcel geometry."
            ),
        )

    # 1. GHOST_STRUCTURE — physically present, no record at all
    if has_structure and not has_record:
        return ClassificationResult(
            parcel_id=inp.parcel_id,
            anomaly_class=AnomalyClass.GHOST_STRUCTURE,
            confidence=round(90 + 10 * inp.match.score, 1),
            rationale=(
                f"nDSM confirms a physical structure "
                f"(match score {inp.match.score:.2f}) with zero corresponding cadastral or revenue record."
            ),
        )

    # 2. PHANTOM_RECORD — record exists, nothing physically there
    if has_record and not has_structure:
        return ClassificationResult(
            parcel_id=inp.parcel_id,
            anomaly_class=AnomalyClass.PHANTOM_RECORD,
            confidence=88.0,
            rationale="Cadastral/revenue record exists for this parcel, but nDSM shows no elevated structure on the ground.",
        )

    # 3. BOUNDARY_DRIFT — matched, but geometries offset within the drift band
    if has_structure and has_record and inp.parcel_coords and inp.structure_coords:
        drift_m = _boundary_drift_margin_m(inp.parcel_coords, inp.structure_coords)
        if settings.DRIFT_MIN_M <= drift_m <= settings.DRIFT_MAX_M:
            return ClassificationResult(
                parcel_id=inp.parcel_id,
                anomaly_class=AnomalyClass.BOUNDARY_DRIFT,
                confidence=92.0,
                rationale=f"Recorded boundary diverges from the physical survey footprint by {drift_m:.1f}m.",
                drift_margin_m=round(drift_m, 1),
            )

    # 4. ATTRIBUTE_MISMATCH — geometry matches fine, attribute fields conflict
    if has_structure and has_record and inp.attribute_conflict_fields:
        return ClassificationResult(
            parcel_id=inp.parcel_id,
            anomaly_class=AnomalyClass.ATTRIBUTE_MISMATCH,
            confidence=85.0,
            rationale=(
                f"Geometries align (IoU {inp.match.iou:.2f}), but "
                f"{', '.join(inp.attribute_conflict_fields)} conflict between revenue and GIS layers."
            ),
        )

    # Clean parcel
    return ClassificationResult(
        parcel_id=inp.parcel_id,
        anomaly_class=AnomalyClass.VERIFIED,
        confidence=round(95 + 5 * inp.match.score, 1) if has_structure else 99.0,
        rationale="Ground truth aligns with official records across geometry, elevation, and attributes.",
    )
