"""
Central settings, env-driven. `DATA_BACKEND=memory` (default) needs nothing else
and is what powers the offline hackathon demo; `DATA_BACKEND=postgis` activates
the SQLAlchemy/GeoAlchemy2 models in app/db/models.py for the full pipeline.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- backend selection ---
    DATA_BACKEND: str = "memory"  # "memory" | "postgis"

    # --- postgis ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "nazar"
    DB_USER: str = "nazar"
    DB_PASSWORD: str = "nazar"

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # --- Module B: nDSM building extraction ---
    NDSM_HEIGHT_THRESHOLD_M: float = 2.5

    # --- Module C: spatial matching engine (weights must sum to ~1.0) ---
    SPATIAL_MATCH_THRESHOLD: float = 0.65
    MATCH_WEIGHT_IOU: float = 0.40
    MATCH_WEIGHT_CENTROID: float = 0.25
    MATCH_WEIGHT_AREA: float = 0.15
    MATCH_WEIGHT_ATTRIBUTE: float = 0.20

    # --- Module D: boundary drift band (meters) that counts as YELLOW ---
    DRIFT_MIN_M: float = 1.0
    DRIFT_MAX_M: float = 3.0

    # --- Module F: synthetic dataset ---
    SYNTHETIC_PARCEL_COUNT: int = 400
    SYNTHETIC_ANOMALY_COUNT: int = 40
    SYNTHETIC_SEED: int = 42
    SYNTHETIC_CENTER_LAT: float = 28.5355
    SYNTHETIC_CENTER_LNG: float = 77.3910

    # --- CORS ---
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()
