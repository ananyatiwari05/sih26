from fastapi import APIRouter
from pydantic import BaseModel

from app.db.memory_store import store

router = APIRouter()


class SyntheticGenerateRequest(BaseModel):
    parcel_count: int | None = None
    anomaly_count: int | None = None
    seed: int | None = None


@router.post("/synthetic/generate", tags=["demo"])
def regenerate_synthetic_dataset(req: SyntheticGenerateRequest):
    """Module F: re-run the offline demo dataset generator with new parameters
    (e.g. a different seed for a fresh set of planted anomalies)."""
    store.reseed(
        parcel_count=req.parcel_count,
        anomaly_count=req.anomaly_count,
        seed=req.seed,
    )
    return {"status": "regenerated", "summary": store.summary}
