from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title="NAZAR 2.0 — Ground Truth Engine API",
    description="Backend & ML pipeline for the SVAMITVA cadastral anomaly detection map (SIH 2026).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "nazar-backend", "data_backend": settings.DATA_BACKEND}


@app.on_event("startup")
def on_startup():
    # Touch the in-memory store so Module F's synthetic dataset (400 parcels,
    # ~40 anomalies, a genuine SHA-256 ledger) is ready the instant /map/layers
    # or /ledger is called — no separate seeding step needed for the demo.
    if settings.DATA_BACKEND == "memory":
        from app.db.memory_store import store  # noqa: F401
