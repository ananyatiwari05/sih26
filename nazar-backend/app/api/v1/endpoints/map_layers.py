from fastapi import APIRouter, Query
from typing import Optional

from app.services.map_service import get_map_layers

router = APIRouter()


@router.get("/map/layers", tags=["map"])
def map_layers(
    anomaly_type: Optional[str] = Query(None, description="Filter to a single anomaly class"),
    epoch: Optional[str] = Query(None, description="Timeline epoch filter")
):
    """
    Serves the map UI: normalized GeoJSON FeatureCollections for all parcels,
    the disputed-only subset, and verified-only subset, plus a color legend —
    this is what nazar-frontend's MapCanvas.jsx should fetch instead of
    importing the local mockData.js.
    """
    return get_map_layers(anomaly_type, epoch)
