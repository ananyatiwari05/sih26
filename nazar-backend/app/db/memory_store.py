"""
Demo-mode ("DATA_BACKEND=memory") data store: a process-local dict seeded from
Module F on startup. Good enough for an offline hackathon demo; swap for the
SQLAlchemy/GeoAlchemy2 models in app/db/models.py when DATA_BACKEND=postgis.
"""
from __future__ import annotations
from threading import Lock

from app.data.inject_conflicts import generate_dataset


class MemoryStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._dataset: dict = {}
        self.reseed()

    def reseed(self, **kwargs) -> None:
        with self._lock:
            self._dataset = generate_dataset(**kwargs)

    @property
    def feature_collection(self) -> dict:
        return self._dataset["geoJsonData"]

    @property
    def features(self) -> list[dict]:
        return self._dataset["geoJsonData"]["features"]

    @property
    def elevation_profiles(self) -> dict:
        return self._dataset["elevationProfiles"]

    @property
    def summary(self) -> dict:
        return self._dataset["summary"]

    def get_feature(self, feature_id: str) -> dict | None:
        for feat in self.features:
            if feat["properties"]["id"] == feature_id:
                return feat
        return None

    def set_feature_status(self, feature_id: str, status: str) -> bool:
        feat = self.get_feature(feature_id)
        if feat is None:
            return False
        feat["properties"]["status"] = status
        return True

    def replace_feature_geometry(self, feature_id: str, geometry: dict) -> bool:
        feat = self.get_feature(feature_id)
        if feat is None:
            return False
        feat["geometry"] = geometry
        return True


store = MemoryStore()
