"""Builds the Evidence Case payload and applies officer actions (Accept/Edit/Reject)."""
from fastapi import HTTPException

from app.db.memory_store import store
from app.ledger.hash_chain import ledger
from app.pipeline.trust_engine import trust_engine
from app.schemas.anomaly import EvidenceCase, ActionRequest, ActionResponse, ElevationPoint


def get_evidence_case(feature_id: str) -> EvidenceCase:
    feat = store.get_feature(feature_id)
    if feat is None:
        raise HTTPException(status_code=404, detail=f"No parcel/anomaly found with id '{feature_id}'")

    props = feat["properties"]
    elevation = store.elevation_profiles.get(feature_id)

    rationale = props.get("description", "")
    if props.get("conflictFields"):
        rationale += f" Conflicting fields: {', '.join(props['conflictFields'])}."
    if props.get("duplicateIds"):
        rationale += f" Duplicate record IDs: {', '.join(props['duplicateIds'])}."
    if props.get("epochPresence"):
        rationale += f" Epoch presence: {props['epochPresence']}."

    return EvidenceCase(
        id=props["id"],
        type=props["type"],
        description=props.get("description", ""),
        confidence=props.get("confidence", 0.0),
        status=props.get("status", "UNKNOWN"),
        surveyYear=props.get("surveyYear", 2026),
        area=props.get("area"),
        height=props.get("height"),
        driftMargin=props.get("driftMargin"),
        owner=props.get("owner"),
        elevationProfile=[ElevationPoint(**p) for p in elevation] if elevation else None,
        rationale=rationale.strip(),
    )


def apply_action(feature_id: str, req: ActionRequest) -> ActionResponse:
    feat = store.get_feature(feature_id)
    if feat is None:
        raise HTTPException(status_code=404, detail=f"No parcel/anomaly found with id '{feature_id}'")

    action = req.action.upper()
    if action == "ACCEPT":
        new_status = "VERIFIED_BY_OFFICER"
        trust_engine.record_feedback(source_id="drone_survey_2026", accepted=True)
    elif action == "REJECT":
        new_status = "REJECTED"
        trust_engine.record_feedback(source_id="drone_survey_2026", accepted=False)
    elif action == "EDIT_BOUNDARY":
        if not req.editedGeometry:
            raise HTTPException(status_code=400, detail="editedGeometry is required for EDIT_BOUNDARY")
        store.replace_feature_geometry(feature_id, req.editedGeometry)
        new_status = "BOUNDARY_EDITED"
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action '{req.action}'")

    store.set_feature_status(feature_id, new_status)
    block = ledger.append(officer_id=req.officerId, action=action, parcel_id=feature_id, notes=req.notes)

    return ActionResponse(parcelId=feature_id, newStatus=new_status, ledgerBlock=block.block, ledgerHash=block.hash)
