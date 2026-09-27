from enum import Enum
from typing import Optional
from pydantic import BaseModel


class AnomalyClass(str, Enum):
    """The 6 standardized classes from Module D, plus the clean/no-anomaly state."""
    GHOST_STRUCTURE = "GHOST_STRUCTURE"        # Red    #EF4444
    PHANTOM_RECORD = "PHANTOM_RECORD"          # Orange #F97316
    BOUNDARY_DRIFT = "BOUNDARY_DRIFT"          # Yellow #EAB308
    ATTRIBUTE_MISMATCH = "ATTRIBUTE_MISMATCH"  # Blue   #3B82F6
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"  # Purple #A855F7
    TEMPORAL_GHOST = "TEMPORAL_GHOST"          # Black  #18181B
    VERIFIED = "VERIFIED"                      # clean parcel, no anomaly


ANOMALY_COLOR_HEX = {
    AnomalyClass.GHOST_STRUCTURE: "#EF4444",
    AnomalyClass.PHANTOM_RECORD: "#F97316",
    AnomalyClass.BOUNDARY_DRIFT: "#EAB308",
    AnomalyClass.ATTRIBUTE_MISMATCH: "#3B82F6",
    AnomalyClass.DUPLICATE_IDENTITY: "#A855F7",
    AnomalyClass.TEMPORAL_GHOST: "#18181B",
    AnomalyClass.VERIFIED: "#22C55E",
}


class ElevationPoint(BaseModel):
    distance: float
    ground: float
    structure: float


class EvidenceCase(BaseModel):
    """Payload for GET /api/v1/anomalies/{id} — feeds EvidenceCasePanel.jsx directly."""
    id: str
    type: AnomalyClass
    description: str
    confidence: float
    status: str
    surveyYear: int
    area: Optional[float] = None
    height: Optional[float] = None
    driftMargin: Optional[float] = None
    owner: Optional[str] = None
    orthophotoCropUrl: Optional[str] = None
    elevationProfile: Optional[list[ElevationPoint]] = None
    rationale: str


class ActionRequest(BaseModel):
    action: str            # "ACCEPT" | "REJECT" | "EDIT_BOUNDARY"
    officerId: str
    notes: Optional[str] = None
    editedGeometry: Optional[dict] = None  # required when action == EDIT_BOUNDARY


class ActionResponse(BaseModel):
    parcelId: str
    newStatus: str
    ledgerBlock: int
    ledgerHash: str
