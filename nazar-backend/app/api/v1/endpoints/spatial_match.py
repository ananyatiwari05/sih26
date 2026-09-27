from fastapi import APIRouter, HTTPException

from app.api.v1.endpoints.ingest import get_job
from app.api.v1.endpoints.extract import get_structures
from app.pipeline.spatial_matching import match_parcels_to_structures
from app.schemas.ingest import SpatialMatchResult

router = APIRouter()

# Match results keyed by job_id, consumed by the /classify stage.
_MATCHES: dict[str, list] = {}


def get_matches(job_id: str):
    return _MATCHES.get(job_id, [])


@router.post("/spatial-match/{job_id}", response_model=SpatialMatchResult, tags=["pipeline"])
def run_spatial_match(job_id: str):
    """Module C: S = w1*IoU + w2*Centroid + w3*Edge + w4*Attribute; matches >= threshold."""
    job = get_job(job_id)
    if job is None or job.cadastral is None:
        raise HTTPException(status_code=404, detail=f"Unknown job_id '{job_id}' or missing cadastral data")

    structures = get_structures(job_id)
    if not structures:
        raise HTTPException(status_code=400, detail="No extracted structures — call /extract first")

    parcels = [
        {"id": f["properties"].get("id", f"parcel-{i}"), "coords": f["geometry"]["coordinates"][0],
         "attrs": f["properties"]}
        for i, f in enumerate(job.cadastral.features)
    ]
    structure_dicts = [
        {"id": f"struct-{i}", "coords": s.polygon, "attrs": {"height_max": s.height_max}}
        for i, s in enumerate(structures)
    ]

    matches = match_parcels_to_structures(parcels, structure_dicts)
    _MATCHES[job_id] = matches

    matched = sum(1 for m in matches if m.matched)
    return SpatialMatchResult(
        job_id=job_id,
        pairs_evaluated=len(matches),
        matched=matched,
        unmatched_structures=len(structure_dicts) - matched,
        unmatched_parcels=len(matches) - matched,
    )
