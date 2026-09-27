from fastapi import APIRouter

from app.schemas.ledger import LedgerBlockOut, LedgerVerifyResult
from app.services import ledger_service

router = APIRouter()


@router.get("/ledger", response_model=list[LedgerBlockOut], tags=["ledger"])
def list_ledger():
    """Newest-first block list, matching LedgerViewer.jsx's terminal display."""
    return ledger_service.list_blocks()


@router.get("/ledger/verify", response_model=LedgerVerifyResult, tags=["ledger"])
def verify_ledger():
    """Recomputes the SHA-256 chain and reports whether it's intact."""
    return ledger_service.verify_chain()


@router.post("/ledger/simulate-tamper/{block_no}", response_model=LedgerVerifyResult, tags=["ledger"])
def simulate_tamper(block_no: int):
    """Demo hook for the 'Simulate Data Tampering' button — corrupts one block
    then immediately re-verifies so the UI can show the break."""
    return ledger_service.simulate_tampering(block_no)


@router.post("/ledger/reset", response_model=LedgerVerifyResult, tags=["ledger"])
def reset_tamper():
    return ledger_service.reset_tampering()
