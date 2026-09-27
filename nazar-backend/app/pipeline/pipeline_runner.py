"""
Chains the flowchart's stages together for the full pipeline mode:

    ingest -> standardize -> extract -> spatial-match -> classify -> ledger

Each stage is independently exposed as its own endpoint too (app/api/v1/endpoints/*)
so a caller can drive the pipeline incrementally; this module is the "just run it
all" convenience path.
"""
from __future__ import annotations
from dataclasses import dataclass

from app.pipeline.ingestion import IngestJob
from app.pipeline.standardization import standardize, StandardizationReport
from app.pipeline.extraction import compute_ndsm, extract_building_footprints, ExtractedStructure
from app.pipeline.spatial_matching import match_parcels_to_structures, MatchResult
from app.pipeline.anomaly_classifier import classify, ClassificationInput, ClassificationResult
from app.ledger.hash_chain import ledger


@dataclass
class PipelineRunReport:
    job_id: str
    standardization: StandardizationReport
    structures_found: int
    matches: list[MatchResult]
    classifications: list[ClassificationResult]


def run_full_pipeline(job: IngestJob) -> PipelineRunReport:
    # 1-2: standardize cadastral vectors (CRS, geometry, topology)
    std_report = standardize(job)

    # 3: nDSM -> building footprints (Module B)
    structures: list[ExtractedStructure] = []
    if job.dsm is not None and job.dtm is not None:
        ndsm = compute_ndsm(job.dsm.array, job.dtm.array)
        structures = extract_building_footprints(ndsm, transform=job.dsm.transform)

    parcels_for_matching = [
        {
            "id": feat.get("properties", {}).get("id", f"parcel-{i}"),
            "coords": feat["geometry"]["coordinates"][0],
            "attrs": feat.get("properties", {}),
        }
        for i, feat in enumerate(job.cadastral.features if job.cadastral else [])
    ]
    structures_for_matching = [
        {"id": f"struct-{i}", "coords": s.polygon, "attrs": {"height_max": s.height_max}}
        for i, s in enumerate(structures)
    ]

    # 4: spatial matching engine (Module C)
    matches = match_parcels_to_structures(parcels_for_matching, structures_for_matching)

    # 5: anomaly classification (Module D)
    classifications: list[ClassificationResult] = []
    parcel_lookup = {p["id"]: p for p in parcels_for_matching}
    structure_lookup = {s["id"]: s for s in structures_for_matching}
    for match in matches:
        parcel = parcel_lookup[match.parcel_id]
        structure = structure_lookup.get(match.structure_id) if match.structure_id else None
        result = classify(ClassificationInput(
            parcel_id=match.parcel_id,
            match=match,
            parcel_attrs=parcel["attrs"],
            structure_attrs=structure["attrs"] if structure else {},
            parcel_coords=parcel["coords"],
            structure_coords=structure["coords"] if structure else None,
        ))
        classifications.append(result)

        # 6: immutable ledger — auto-log every newly detected (non-clean) anomaly
        if result.anomaly_class.value != "VERIFIED":
            ledger.append("SYS-AUTO", f"DETECT_{result.anomaly_class.value}", match.parcel_id)

    return PipelineRunReport(
        job_id=job.job_id,
        standardization=std_report,
        structures_found=len(structures),
        matches=matches,
        classifications=classifications,
    )
