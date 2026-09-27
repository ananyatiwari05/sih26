"""
Module C: Spatial Matching Engine.

    S = w1*IoU + w2*CentroidProximity + w3*EdgeAlignment + w4*AttributeAgreement

Matches cadastral parcels against extracted (nDSM/OpenCV) structures. A pair is
"matched" when S >= SPATIAL_MATCH_THRESHOLD; S itself is surfaced to Module D as
the match confidence score.
"""
from __future__ import annotations
from dataclasses import dataclass

from app.config import settings
    polygon_iou,
    centroid_proximity_score,
    area_ratio_score,
    attribute_agreement_score,
)


@dataclass
class MatchResult:
    parcel_id: str
    structure_id: str | None
    score: float
    iou: float
    centroid_score: float
    area_score: float
    attribute_score: float
    matched: bool


def composite_score(
    parcel_coords: list[list[float]],
    structure_coords: list[list[float]] | None,
    parcel_attrs: dict,
    structure_attrs: dict,
    attribute_keys: list[str] | None = None,
) -> tuple[float, float, float, float, float]:
    """Returns (S, iou, centroid_score, area_score, attribute_score).

    When no `attribute_keys` are supplied there is nothing to agree or disagree
    on, so the attribute term is dropped entirely and its weight is
    redistributed proportionally across the three geometric terms — rather
    than defaulting it to "full agreement", which would silently inflate the
    score for every geometry-only comparison.
    """
    if structure_coords is None:
        return 0.0, 0.0, 0.0, 0.0, 0.0

    iou = polygon_iou(parcel_coords, structure_coords)
    centroid_score = centroid_proximity_score(parcel_coords, structure_coords)
    area_score = area_ratio_score(parcel_coords, structure_coords)

    w_iou, w_centroid, w_area, w_attr = (
        settings.MATCH_WEIGHT_IOU,
        settings.MATCH_WEIGHT_CENTROID,
        settings.MATCH_WEIGHT_AREA,
        settings.MATCH_WEIGHT_ATTRIBUTE,
    )

    if attribute_keys:
        attribute_score = attribute_agreement_score(parcel_attrs, structure_attrs, attribute_keys)
        s = w_iou * iou + w_centroid * centroid_score + w_area * area_score + w_attr * attribute_score
    else:
        attribute_score = 0.0
        geo_weight_total = w_iou + w_centroid + w_area
        s = (w_iou * iou + w_centroid * centroid_score + w_area * area_score) / geo_weight_total

    return s, iou, centroid_score, area_score, attribute_score


def match_parcels_to_structures(
    parcels: list[dict],       # [{id, coords, attrs}]
    structures: list[dict],    # [{id, coords, attrs}]
    attribute_keys: list[str] | None = None,
) -> list[MatchResult]:
    """
    Greedy best-match assignment: for each parcel, pick the highest-scoring
    unclaimed structure. O(n*m) — fine at hackathon/demo scale (hundreds of
    parcels); swap for a Hungarian-algorithm assignment for production scale.
    """
    results: list[MatchResult] = []
    claimed_structures: set[str] = set()

    for parcel in parcels:
        best_score = -1.0
        best = None
        for structure in structures:
            if structure["id"] in claimed_structures:
                continue
            s, iou, cscore, ascore_geom, ascore = composite_score(
                parcel["coords"], structure["coords"], parcel.get("attrs", {}),
                structure.get("attrs", {}), attribute_keys,
            )
            if s > best_score:
                best_score = s
                best = (structure, iou, cscore, ascore_geom, ascore)

        if best is None:
            results.append(MatchResult(parcel["id"], None, 0.0, 0.0, 0.0, 0.0, 0.0, False))
            continue

        structure, iou, cscore, ascore_geom, ascore = best
        matched = best_score >= settings.SPATIAL_MATCH_THRESHOLD
        if matched:
            claimed_structures.add(structure["id"])
        results.append(MatchResult(
            parcel_id=parcel["id"], structure_id=structure["id"], score=best_score,
            iou=iou, centroid_score=cscore, area_score=ascore_geom, attribute_score=ascore,
            matched=matched,
        ))
    return results
