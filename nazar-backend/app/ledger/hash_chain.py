"""
Module E (part 2): Immutable Trust Ledger — SHA-256 append-only hash chain.

    block_n.hash = SHA256(block_n.data + block_(n-1).hash)

Every officer action (ACCEPT / REJECT / EDIT_BOUNDARY / SYSTEM auto-events like
DRONE_SYNC) appends a block. `verify()` walks the whole chain recomputing hashes
from scratch and comparing them to what's stored, to flag tampering — this is
exactly what GET /api/v1/ledger/verify and the frontend's "Simulate Data
Tampering" button in LedgerViewer.jsx exercise.

Internally we keep the *full* 64-hex-char SHA-256 digest for every block (that's
what's actually chained and re-verified). `LedgerBlock.hash`/`.prevHash` hold a
truncated display form ("a4f8...9c3b") matching the frontend's terminal-style
ledger UI and its `initialLedgerData` mock (genesis prevHash renders as
"0000...0000", identical to the truncation of 64 zero-hex-chars).
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

GENESIS_FULL_HASH = "0" * 64


@dataclass
class LedgerBlock:
    block: int
    officerId: str
    action: str
    parcelId: str
    timestamp: str
    prevHash: str
    hash: str = ""
    tampered: bool = False
    notes: str | None = None

    def payload_for_hash(self) -> str:
        """Everything except `hash`/`tampered` — the data half of block_n.hash = SHA256(data + prevHash)."""
        payload = {
            "block": self.block,
            "officerId": self.officerId,
            "action": self.action,
            "parcelId": self.parcelId,
            "timestamp": self.timestamp,
            "notes": self.notes,
        }
        return json.dumps(payload, sort_keys=True)


def _short_hash(full_hex: str) -> str:
    """Frontend displays truncated hashes like 'a4f8...9c3b'; we keep the full
    hash server-side (in HashChain._full_hashes) for real verification and only
    shorten for the *display* fields (`hash`, `prevHash`)."""
    return f"{full_hex[:4]}...{full_hex[-4:]}"


def _compute_full_hash(payload: str, prev_full_hash: str) -> str:
    return hashlib.sha256((payload + prev_full_hash).encode("utf-8")).hexdigest()


class HashChain:
    """Append-only chain, oldest-first internally. `list_desc()` reverses for the
    frontend's newest-first terminal display."""

    def __init__(self) -> None:
        self._blocks: list[LedgerBlock] = []
        self._full_hashes: dict[int, str] = {}
        self._corrupted: set[int] = set()

    def append(self, officer_id: str, action: str, parcel_id: str, notes: str | None = None) -> LedgerBlock:
        block_no = len(self._blocks) + 101  # matches frontend mock's starting numbering (101, 102, ...)
        prev_full = self._full_hashes[self._blocks[-1].block] if self._blocks else GENESIS_FULL_HASH

        block = LedgerBlock(
            block=block_no,
            officerId=officer_id,
            action=action,
            parcelId=parcel_id,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            prevHash=_short_hash(prev_full),
            notes=notes,
        )
        full_hash = _compute_full_hash(block.payload_for_hash(), prev_full)
        block.hash = _short_hash(full_hash)

        self._full_hashes[block_no] = full_hash
        self._blocks.append(block)
        return block

    def tamper(self, block_no: int) -> None:
        """Demo hook for the frontend's 'Simulate Data Tampering' button: marks one
        block's stored hash as corrupted so `verify()` reports a broken chain from
        there back (mirrors LedgerViewer.jsx's simulateTampering, which also flags
        every earlier block as visually 'tampered' since they're now unverifiable
        relative to a corrupted ancestor)."""
        target = next((b for b in self._blocks if b.block == block_no), None)
        if target is None:
            raise ValueError(f"No ledger block #{block_no}")

        self._corrupted.add(block_no)
        target.hash = "ERR_HASH_MISMATCH"
        target.tampered = True

        idx = self._blocks.index(target)
        for b in self._blocks[:idx]:
            b.tampered = True

    def reset_tamper(self) -> None:
        self._corrupted.clear()
        for b in self._blocks:
            b.tampered = False
            b.hash = _short_hash(self._full_hashes[b.block])

    def verify(self) -> tuple[bool, int | None, str]:
        """Recomputes every block's hash from (data + previous block's *actual*
        stored full hash) and compares against what's stored. Returns
        (is_valid, broken_at_block, message)."""
        prev_full = GENESIS_FULL_HASH
        for block in self._blocks:
            if block.block in self._corrupted:
                return False, block.block, f"Chain integrity broken at block {block.block}: hash mismatch."

            expected_full = _compute_full_hash(block.payload_for_hash(), prev_full)
            stored_full = self._full_hashes.get(block.block)
            if stored_full != expected_full:
                return False, block.block, f"Chain integrity broken at block {block.block}: hash mismatch."
            prev_full = stored_full

        return True, None, "Chain verified: all blocks intact, no tampering detected."

    def list_desc(self) -> list[LedgerBlock]:
        """Newest first, matching LedgerViewer.jsx's initialLedgerData ordering."""
        return list(reversed(self._blocks))

    def to_dict_list(self) -> list[dict]:
        return [asdict(b) for b in self.list_desc()]


ledger = HashChain()
