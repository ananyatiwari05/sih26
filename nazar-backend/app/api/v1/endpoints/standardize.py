from fastapi import APIRouter, HTTPException

from app.api.v1.endpoints.ingest import get_job
from app.pipeline.standardization import standardize
from app.schemas.ingest import StandardizeResult

router = APIRouter()


@router.post("/standardize/{job_id}", response_model=StandardizeResult, tags=["pipeline"])
def run_standardize(job_id: str):
    """CRS Detection -> CRS Transformation -> Geometry Validation -> Topology Correction."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Unknown job_id '{job_id}' — call /ingest first")

    report = standardize(job)
    return StandardizeResult(
        job_id=job_id,
        source_crs=report.source_crs,
        target_crs=report.target_crs,
        reprojected=report.reprojected,
        geometries_validated=report.geometries_validated,
        geometries_repaired=report.geometries_repaired,
        topology_issues_fixed=report.topology_issues_fixed,
    )
