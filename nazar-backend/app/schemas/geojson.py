"""
Minimal GeoJSON Pydantic models — deliberately loose (Dict for geometry.coordinates)
so any Polygon/MultiPolygon/Point survives round-tripping to the frontend, which
consumes these directly as `feature.geometry.coordinates` / `feature.properties.*`
(see nazar-frontend/src/components/MapCanvas.jsx).
"""
from typing import Any, Literal
from pydantic import BaseModel, Field


class Geometry(BaseModel):
    type: Literal["Polygon", "MultiPolygon", "Point"]
    coordinates: Any


class Feature(BaseModel):
    type: Literal["Feature"] = "Feature"
    properties: dict[str, Any] = Field(default_factory=dict)
    geometry: Geometry


class FeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[Feature]
