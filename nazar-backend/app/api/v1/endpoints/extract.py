from fastapi import APIRouter, HTTPException

from app.api.v1.endpoints.ingest import get_job
from app.pipeline.extraction import compute_ndsm, extract_building_footprints, simplify_parcel_boundary
from app.schemas.ingest import ExtractResult
from app.config import settings

router = APIRouter()

# Extracted structures keyed by job_id, consumed by the /spatial-match stage.
_STRUCTURES: dict[str, list] = {}


def get_structures(job_id: str):
    return _STRUCTURES.get(job_id, [])


@router.post("/extract/{job_id}", response_model=ExtractResult, tags=["pipeline"])
def run_extract(job_id: str, height_threshold_m: float | None = None):
    """Module B: nDSM = DSM - DTM, threshold + OpenCV -> building footprints;
    also simplifies cadastral parcel boundaries (Parcel Cleanup)."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Unknown job_id '{job_id}' — call /ingest first")
    if job.dsm is None or job.dtm is None:
        raise HTTPException(status_code=400, detail="Both dsm_file and dtm_file are required for extraction")

    ndsm = compute_ndsm(job.dsm.array, job.dtm.array)
    structures = extract_building_footprints(
        ndsm, transform=job.dsm.transform, height_threshold_m=height_threshold_m
    )
    _STRUCTURES[job_id] = structures

    cleaned_count = 0
    if job.cadastral is not None:
        for feat in job.cadastral.features:
            try:
                feat["geometry"]["coordinates"][0] = simplify_parcel_boundary(
                    feat["geometry"]["coordinates"][0]
                )
                cleaned_count += 1
            except Exception:
                continue  # leave malformed geometries untouched; standardize() should catch these earlier

    return ExtractResult(
        job_id=job_id,
        ndsm_threshold_m=height_threshold_m or settings.NDSM_HEIGHT_THRESHOLD_M,
        structures_extracted=len(structures),
        parcels_cleaned=cleaned_count,
    )
