from pydantic import BaseModel


class LedgerBlockOut(BaseModel):
    """Matches nazar-frontend/src/components/LedgerViewer.jsx field-for-field."""
    block: int
    hash: str
    prevHash: str
    timestamp: str
    officerId: str
    action: str
    parcelId: str
    tampered: bool = False


class LedgerVerifyResult(BaseModel):
    valid: bool
    totalBlocks: int
    brokenAtBlock: int | None = None
    message: str
