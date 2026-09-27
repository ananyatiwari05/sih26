from fastapi import APIRouter

from app.api.v1.endpoints import (
    ingest, standardize, extract, spatial_match, classify,
    map_layers, anomalies, ledger, synthetic,
    query, parcels,
)

api_router = APIRouter()

api_router.include_router(ingest.router)
api_router.include_router(standardize.router)
api_router.include_router(extract.router)
api_router.include_router(spatial_match.router)
api_router.include_router(classify.router)
api_router.include_router(map_layers.router)
api_router.include_router(anomalies.router)
api_router.include_router(ledger.router)
api_router.include_router(synthetic.router)
api_router.include_router(query.router)
api_router.include_router(parcels.router)
