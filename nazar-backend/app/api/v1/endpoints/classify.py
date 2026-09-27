from fastapi import APIRouter, HTTPException

from app.api.v1.endpoints.ingest import get_job
from app.api.v1.endpoints.spatial_match import get_matches
from app.api.v1.endpoints.extract import get_structures
from app.pipeline.anomaly_classifier import classify, ClassificationInput
from app.schemas.ingest import ClassifyResult
from app.ledger.hash_chain import ledger

router = APIRouter()


@router.post("/classify/{job_id}", response_model=ClassifyResult, tags=["pipeline"])
def run_classify(job_id: str):
    """Module D: assigns each parcel one of the 6 anomaly classes (or VERIFIED)
    and appends a ledger block for every anomaly newly detected."""
    job = get_job(job_id)
    matches = get_matches(job_id)
    structures = get_structures(job_id)
    if job is None or job.cadastral is None:
        raise HTTPException(status_code=404, detail=f"Unknown job_id '{job_id}'")
    if not matches:
        raise HTTPException(status_code=400, detail="No match results — call /spatial-match first")

    parcel_lookup = {
        f["properties"].get("id", f"parcel-{i}"): f
        for i, f in enumerate(job.cadastral.features)
    }
    structure_lookup = {f"struct-{i}": s for i, s in enumerate(structures)}

    breakdown: dict[str, int] = {}
    for match in matches:
        parcel_feat = parcel_lookup[match.parcel_id]
        structure = structure_lookup.get(match.structure_id) if match.structure_id else None

        result = classify(ClassificationInput(
            parcel_id=match.parcel_id,
            match=match,
            parcel_attrs=parcel_feat["properties"],
            structure_attrs={"height_max": structure.height_max} if structure else {},
            parcel_coords=parcel_feat["geometry"]["coordinates"][0],
            structure_coords=structure.polygon if structure else None,
        ))

        parcel_feat["properties"]["type"] = result.anomaly_class.value
        parcel_feat["properties"]["confidence"] = result.confidence
        parcel_feat["properties"]["rationale"] = result.rationale
        breakdown[result.anomaly_class.value] = breakdown.get(result.anomaly_class.value, 0) + 1

        if result.anomaly_class.value != "VERIFIED":
            ledger.append("SYS-AUTO", f"DETECT_{result.anomaly_class.value}", match.parcel_id)

    anomalies_found = sum(v for k, v in breakdown.items() if k != "VERIFIED")
    return ClassifyResult(job_id=job_id, anomalies_found=anomalies_found, breakdown=breakdown)
