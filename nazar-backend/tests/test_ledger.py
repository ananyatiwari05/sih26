from app.ledger.hash_chain import HashChain


def test_chain_starts_valid():
    chain = HashChain()
    chain.append("SYS-AUTO", "DRONE_SYNC", "BATCH-A")
    chain.append("OFF-1", "FLAG_GHOST", "GHOST-100")
    valid, broken_at, _ = chain.verify()
    assert valid is True
    assert broken_at is None


def test_tampering_is_detected():
    chain = HashChain()
    chain.append("SYS-AUTO", "DRONE_SYNC", "BATCH-A")
    b2 = chain.append("OFF-1", "FLAG_GHOST", "GHOST-100")
    chain.append("OFF-1", "VERIFY_PARCEL", "VERIFIED-400")

    chain.tamper(b2.block)
    valid, broken_at, message = chain.verify()

    assert valid is False
    assert broken_at == b2.block
    assert "broken" in message.lower()


def test_reset_restores_validity():
    chain = HashChain()
    b1 = chain.append("SYS-AUTO", "DRONE_SYNC", "BATCH-A")
    chain.tamper(b1.block)
    assert chain.verify()[0] is False

    chain.reset_tamper()
    valid, broken_at, _ = chain.verify()
    assert valid is True
    assert broken_at is None


def test_blocks_are_chained_by_prev_hash():
    chain = HashChain()
    b1 = chain.append("SYS-AUTO", "DRONE_SYNC", "BATCH-A")
    b2 = chain.append("OFF-1", "FLAG_GHOST", "GHOST-100")
    assert b2.prevHash == b1.hash
