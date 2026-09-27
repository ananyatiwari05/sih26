from fastapi import APIRouter, UploadFile, File
from typing import Optional

from app.pipeline.ingestion import (
    IngestJob, ingest_cadastral_geojson, ingest_raster_geotiff,
    ingest_revenue_csv, ingest_revenue_json,
)
from app.schemas.ingest import IngestManifest

router = APIRouter()

# In-memory job registry for the incremental (stage-by-stage) pipeline mode.
_JOBS: dict[str, IngestJob] = {}


def get_job(job_id: str) -> IngestJob | None:
    return _JOBS.get(job_id)


@router.post("/ingest", response_model=IngestManifest, tags=["pipeline"])
async def ingest(
    cadastral_file: Optional[UploadFile] = File(None, description="Cadastral GeoJSON/Shapefile"),
    dsm_file: Optional[UploadFile] = File(None, description="Drone DSM GeoTIFF"),
    dtm_file: Optional[UploadFile] = File(None, description="Drone DTM GeoTIFF"),
    revenue_file: Optional[UploadFile] = File(None, description="Revenue CSV/JSON"),
):
    """Module A: Multi-Source Input. Accepts any subset of the 4 sources; a job_id
    ties them together for the next pipeline stages."""
    job = IngestJob()

    if cadastral_file is not None:
        raw = await cadastral_file.read()
        job.cadastral = ingest_cadastral_geojson(raw, cadastral_file.filename)

    if dsm_file is not None:
        raw = await dsm_file.read()
        job.dsm = ingest_raster_geotiff(raw, dsm_file.filename)

    if dtm_file is not None:
        raw = await dtm_file.read()
        job.dtm = ingest_raster_geotiff(raw, dtm_file.filename)

    if revenue_file is not None:
        raw = await revenue_file.read()
        if revenue_file.filename.lower().endswith(".json"):
            job.revenue = ingest_revenue_json(raw, revenue_file.filename)
        else:
            job.revenue = ingest_revenue_csv(raw, revenue_file.filename)

    _JOBS[job.job_id] = job

    return IngestManifest(
        job_id=job.job_id,
        cadastral_filename=job.cadastral.filename if job.cadastral else None,
        dsm_filename=job.dsm.filename if job.dsm else None,
        dtm_filename=job.dtm.filename if job.dtm else None,
        revenue_filename=job.revenue.filename if job.revenue else None,
        detected_crs=job.cadastral.source_crs if job.cadastral else None,
        feature_count=len(job.cadastral.features) if job.cadastral else None,
    )
