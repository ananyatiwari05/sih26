from typing import Optional
from pydantic import BaseModel


class IngestManifest(BaseModel):
    """
    Returned by POST /api/v1/ingest. File bytes are streamed via multipart form
    fields (cadastral_file, dsm_file, dtm_file, revenue_file) — this manifest is
    the receipt that downstream stages (standardize/extract) reference by job_id.
    """
    job_id: str
    cadastral_filename: Optional[str] = None
    dsm_filename: Optional[str] = None
    dtm_filename: Optional[str] = None
    revenue_filename: Optional[str] = None
    detected_crs: Optional[str] = None
    feature_count: Optional[int] = None
    status: str = "INGESTED"


class StandardizeResult(BaseModel):
    job_id: str
    source_crs: Optional[str]
    target_crs: str = "EPSG:4326"
    reprojected: bool
    geometries_validated: int
    geometries_repaired: int
    topology_issues_fixed: int


class ExtractResult(BaseModel):
    job_id: str
    ndsm_threshold_m: float
    structures_extracted: int
    parcels_cleaned: int


class SpatialMatchResult(BaseModel):
    job_id: str
    pairs_evaluated: int
    matched: int
    unmatched_structures: int
    unmatched_parcels: int


class ClassifyResult(BaseModel):
    job_id: str
    anomalies_found: int
    breakdown: dict[str, int]
