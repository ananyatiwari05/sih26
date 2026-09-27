from fastapi import APIRouter

from app.schemas.anomaly import EvidenceCase, ActionRequest, ActionResponse
from app.services.anomaly_service import get_evidence_case, apply_action

router = APIRouter()


@router.get("/anomalies/{feature_id}", response_model=EvidenceCase, tags=["anomalies"])
def read_anomaly(feature_id: str):
    """Evidence Case payload feeding EvidenceCasePanel.jsx: rationale, confidence,
    nDSM height profile (for Ghost/Drift), and current status."""
    return get_evidence_case(feature_id)


@router.post("/anomalies/{feature_id}/action", response_model=ActionResponse, tags=["anomalies"])
def act_on_anomaly(feature_id: str, action: ActionRequest):
    """Human-in-the-loop Accept / Reject / Edit Boundary — appends a block to the
    immutable trust ledger and updates the officer's source-trust score."""
    return apply_action(feature_id, action)
