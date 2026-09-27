"""
Module A (part 2): Data Standardization.

  CRS Detection -> CRS Transformation -> Geometry Validation -> Topology Correction

Runs on the IngestJob produced by ingestion.py. Vector work uses shapely/geopandas,
raster CRS work uses pyproj/rasterio. All heavy imports are lazy so the module can
be imported (and unit-tested) without GDAL present.
"""
from __future__ import annotations
from dataclasses import dataclass

from app.pipeline.ingestion import IngestJob, IngestedVector
from app.config import settings

TARGET_CRS = "EPSG:4326"


@dataclass
class StandardizationReport:
    source_crs: str | None
    target_crs: str
    reprojected: bool
    geometries_validated: int
    geometries_repaired: int
    topology_issues_fixed: int


def detect_crs(vector: IngestedVector) -> str | None:
    """Best-effort CRS sniff: explicit CRS block, else assume WGS84 for lat/lng-range coords."""
    if vector.source_crs:
        return vector.source_crs
    return "EPSG:4326"  # assume already geographic if unspecified (common for GeoJSON)


def reproject_to_wgs84(vector: IngestedVector) -> tuple[IngestedVector, bool]:
    """Reprojects every feature's geometry to EPSG:4326 if it isn't already."""
    src_crs = detect_crs(vector)
    if src_crs in (None, TARGET_CRS, "EPSG:4326", "urn:ogc:def:crs:OGC:1.3:CRS84"):
        return vector, False

    try:
        import geopandas as gpd
        from shapely.geometry import shape, mapping
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("geopandas/shapely required for reprojection") from exc

    geoms = [shape(f["geometry"]) for f in vector.features]
    gdf = gpd.GeoDataFrame(
        [f.get("properties", {}) for f in vector.features],
        geometry=geoms,
        crs=src_crs,
    ).to_crs(TARGET_CRS)

    reprojected_features = []
    for feat, geom in zip(vector.features, gdf.geometry):
        new_feat = dict(feat)
        new_feat["geometry"] = mapping(geom)
        reprojected_features.append(new_feat)

    return IngestedVector(features=reprojected_features, source_crs=TARGET_CRS,
                           filename=vector.filename), True


def validate_and_repair_geometry(vector: IngestedVector) -> tuple[IngestedVector, int, int, int]:
    """
    Geometry Validation + Topology Correction: fixes self-intersections, strips
    duplicate consecutive coordinates, closes unclosed rings. Uses shapely's
    `make_valid` (standard, cheap self-intersection repair).

    Returns (cleaned_vector, validated_count, repaired_count, topology_fixed_count).
    """
    try:
        from shapely.geometry import shape, mapping
        from shapely.validation import make_valid
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("shapely required for geometry validation") from exc

    validated = 0
    repaired = 0
    topology_fixed = 0
    out_features = []

    for feat in vector.features:
        validated += 1
        geom = shape(feat["geometry"])

        # Strip duplicate consecutive coordinates (topology cleanup)
        coords = list(geom.exterior.coords) if geom.geom_type == "Polygon" else None
        if coords:
            deduped = [coords[0]] + [c for i, c in enumerate(coords[1:], 1) if c != coords[i - 1]]
            if len(deduped) != len(coords):
                topology_fixed += 1
                geom = geom.__class__(deduped) if len(deduped) >= 4 else geom

        if not geom.is_valid:
            geom = make_valid(geom)
            repaired += 1

        new_feat = dict(feat)
        new_feat["geometry"] = mapping(geom)
        out_features.append(new_feat)

    cleaned = IngestedVector(features=out_features, source_crs=vector.source_crs, filename=vector.filename)
    return cleaned, validated, repaired, topology_fixed


def standardize(job: IngestJob) -> StandardizationReport:
    if job.cadastral is None:
        return StandardizationReport(None, TARGET_CRS, False, 0, 0, 0)

    src_crs = detect_crs(job.cadastral)
    reprojected_vector, did_reproject = reproject_to_wgs84(job.cadastral)
    cleaned_vector, validated, repaired, topology_fixed = validate_and_repair_geometry(reprojected_vector)

    job.cadastral = cleaned_vector
    return StandardizationReport(
        source_crs=src_crs,
        target_crs=TARGET_CRS,
        reprojected=did_reproject,
        geometries_validated=validated,
        geometries_repaired=repaired,
        topology_issues_fixed=topology_fixed,
    )
