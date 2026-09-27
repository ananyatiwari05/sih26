"""
ORM models for `DATA_BACKEND=postgis` — the full pipeline mode backing real
cadastral/drone/revenue data. Requires `CREATE EXTENSION postgis;` on the DB.
Not used by the default in-memory demo (see app/db/memory_store.py).
"""
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(String, primary_key=True)          # e.g. cadastral survey number
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    owner = Column(String, nullable=True)
    land_use = Column(String, nullable=True)
    area_sqm = Column(Float, nullable=True)
    survey_year = Column(Integer, nullable=True)
    source_job_id = Column(String, nullable=True)
    attrs = Column(JSON, default=dict)

    anomalies = relationship("Anomaly", back_populates="parcel")


class Structure(Base):
    """A building footprint extracted from nDSM + OpenCV (Module B)."""
    __tablename__ = "structures"

    id = Column(String, primary_key=True)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    height_max = Column(Float, nullable=False)
    height_mean = Column(Float, nullable=False)
    area_sqm = Column(Float, nullable=False)
    survey_epoch = Column(String, nullable=True)   # e.g. "2026-Q2"
    source_job_id = Column(String, nullable=True)


class Anomaly(Base):
    """Output of Module D — one row per classified parcel/structure pair."""
    __tablename__ = "anomalies"

    id = Column(String, primary_key=True)
    parcel_id = Column(String, ForeignKey("parcels.id"), nullable=False)
    structure_id = Column(String, ForeignKey("structures.id"), nullable=True)
    anomaly_class = Column(String, nullable=False)   # AnomalyClass enum value
    confidence = Column(Float, nullable=False)
    rationale = Column(String, nullable=False)
    drift_margin_m = Column(Float, nullable=True)
    status = Column(String, default="OPEN")          # OPEN | ACCEPTED | REJECTED | EDITED
    created_at = Column(DateTime, default=datetime.utcnow)

    parcel = relationship("Parcel", back_populates="anomalies")


class LedgerBlockRow(Base):
    """Persisted mirror of app/ledger/hash_chain.py's in-memory chain, so the
    audit trail survives restarts in postgis mode."""
    __tablename__ = "ledger_blocks"

    block = Column(Integer, primary_key=True)
    officer_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    parcel_id = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    prev_hash = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    tampered = Column(Boolean, default=False)
    notes = Column(String, nullable=True)


class SourceTrustRow(Base):
    """Persisted mirror of app/pipeline/trust_engine.py for postgis mode."""
    __tablename__ = "source_trust"

    source_id = Column(String, primary_key=True)
    alpha = Column(Float, default=1.0)
    beta = Column(Float, default=1.0)
