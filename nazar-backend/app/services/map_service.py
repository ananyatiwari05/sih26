"""Builds the GET /api/v1/map/layers response the frontend's MapCanvas.jsx renders."""
from app.db.memory_store import store
from app.schemas.anomaly import AnomalyClass, ANOMALY_COLOR_HEX


def get_map_layers(anomaly_type: str | None = None, epoch: str | None = None) -> dict:
    """
    Returns one FeatureCollection per logical layer so the frontend's
    LayerControls can toggle them independently, plus the flat combined
    collection (`all`) that mockData.js currently ships as a single list.
    """
    features = store.features
    if anomaly_type:
        features = [f for f in features if f["properties"]["type"] == anomaly_type]
    
    if epoch:
        features = [
            f for f in features
            if f["properties"].get("epochPresence", {}).get(epoch, True)
        ]

    disputed_types = {c.value for c in AnomalyClass if c != AnomalyClass.VERIFIED}
    disputed = [f for f in features if f["properties"]["type"] in disputed_types]
    verified = [f for f in features if f["properties"]["type"] == AnomalyClass.VERIFIED.value]

    def fc(feats: list[dict]) -> dict:
        return {"type": "FeatureCollection", "features": feats}

    return {
        "all": fc(features),
        "disputed": fc(disputed),
        "verified": fc(verified),
        "legend": {c.value: ANOMALY_COLOR_HEX[c] for c in AnomalyClass},
        "summary": store.summary,
    }
