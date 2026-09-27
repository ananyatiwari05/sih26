from fastapi import HTTPException

from app.ledger.hash_chain import ledger
from app.schemas.ledger import LedgerBlockOut, LedgerVerifyResult


def list_blocks() -> list[LedgerBlockOut]:
    return [LedgerBlockOut(**b) for b in ledger.to_dict_list()]


def verify_chain() -> LedgerVerifyResult:
    valid, broken_at, message = ledger.verify()
    return LedgerVerifyResult(
        valid=valid, totalBlocks=len(ledger.list_desc()), brokenAtBlock=broken_at, message=message
    )


def simulate_tampering(block_no: int) -> LedgerVerifyResult:
    known_blocks = {b.block for b in ledger.list_desc()}
    if block_no not in known_blocks:
        raise HTTPException(status_code=404, detail=f"No ledger block #{block_no}")
    ledger.tamper(block_no)
    return verify_chain()


def reset_tampering() -> LedgerVerifyResult:
    ledger.reset_tamper()
    return verify_chain()
