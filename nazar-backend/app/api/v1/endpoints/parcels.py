from fastapi import APIRouter

router = APIRouter()

@router.get("/parcels/{feature_id}/property-card", tags=["parcels"])
def get_property_card(feature_id: str):
    # Dummy implementation for Property Card Exporter
    return {
        "id": feature_id,
        "owner": "Ramesh",
        "area": 250.5,
        "status": "Verified"
    }
