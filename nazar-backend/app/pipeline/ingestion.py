"""
Module A (part 1): Multi-Source Input handlers.

Accepts the three source types from the flowchart:
  - Cadastral GIS Shapefile / GeoJSON  -> vector parcels
  - Drone Orthophoto / DSM / DTM GeoTIFF -> raster
  - Revenue Database CSV/JSON           -> tabular attributes

Each handler returns a normalized in-memory representation that
`standardization.py` consumes next. Heavy geo libraries are imported lazily so
this module still loads (and the /ingest endpoint still works for CSV/JSON)
even in environments without GDAL/rasterio installed.
"""
from __future__ import annotations
import csv
import io
import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class IngestedVector:
    features: list[dict]
    source_crs: Optional[str] = None
    filename: Optional[str] = None


@dataclass
class IngestedRaster:
    array: Any                     # numpy ndarray, band 1
    transform: Any                 # affine transform (rasterio)
    crs: Optional[str]
    filename: Optional[str] = None


@dataclass
class IngestedTable:
    rows: list[dict]
    filename: Optional[str] = None


@dataclass
class IngestJob:
    job_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    cadastral: Optional[IngestedVector] = None
    dsm: Optional[IngestedRaster] = None
    dtm: Optional[IngestedRaster] = None
    revenue: Optional[IngestedTable] = None


def ingest_cadastral_geojson(raw_bytes: bytes, filename: str) -> IngestedVector:
    data = json.loads(raw_bytes.decode("utf-8"))
    features = data.get("features", [data]) if isinstance(data, dict) else data
    crs = None
    if isinstance(data, dict):
        crs_block = data.get("crs", {})
        crs = crs_block.get("properties", {}).get("name")
    return IngestedVector(features=features, source_crs=crs, filename=filename)


def ingest_cadastral_shapefile(raw_bytes: bytes, filename: str) -> IngestedVector:
    """Requires geopandas/fiona; shapefiles arrive zipped (.shp/.shx/.dbf/.prj)."""
    try:
        import geopandas as gpd
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("geopandas is required to read Shapefiles (`pip install geopandas`)") from exc

    with io.BytesIO(raw_bytes) as buf:
        gdf = gpd.read_file(buf)
    crs = gdf.crs.to_string() if gdf.crs else None
    features = json.loads(gdf.to_json())["features"]
    return IngestedVector(features=features, source_crs=crs, filename=filename)


def ingest_raster_geotiff(raw_bytes: bytes, filename: str) -> IngestedRaster:
    """DSM or DTM GeoTIFF -> single-band ndarray + affine transform + CRS."""
    try:
        import rasterio
        from rasterio.io import MemoryFile
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("rasterio is required to read GeoTIFFs (`pip install rasterio`)") from exc

    with MemoryFile(raw_bytes) as memfile:
        with memfile.open() as dataset:
            array = dataset.read(1)
            transform = dataset.transform
            crs = dataset.crs.to_string() if dataset.crs else None
    return IngestedRaster(array=array, transform=transform, crs=crs, filename=filename)


def ingest_revenue_csv(raw_bytes: bytes, filename: str) -> IngestedTable:
    text = raw_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return IngestedTable(rows=list(reader), filename=filename)


def ingest_revenue_json(raw_bytes: bytes, filename: str) -> IngestedTable:
    data = json.loads(raw_bytes.decode("utf-8"))
    rows = data if isinstance(data, list) else data.get("records", [])
    return IngestedTable(rows=rows, filename=filename)
