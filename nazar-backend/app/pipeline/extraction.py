"""
Module B: Physical Extraction Pipeline (Computer Vision & Elevation).

  nDSM = DSM - DTM
  mask = nDSM > threshold (default 2.5m)
  OpenCV connected components / contours -> building footprint polygons
  Parcel Cleanup: boundary simplification (shapely.simplify) on cadastral vectors
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from app.config import settings


@dataclass
class ExtractedStructure:
    polygon: list[list[float]]   # ring of [lng, lat] (or raster px coords if no transform)
    height_max: float
    height_mean: float
    area: float
    centroid: tuple[float, float]


def compute_ndsm(dsm_array, dtm_array):
    """nDSM = DSM (surface, incl. buildings/canopy) - DTM (bare terrain)."""
    import numpy as np
    if dsm_array.shape != dtm_array.shape:
        raise ValueError(f"DSM/DTM shape mismatch: {dsm_array.shape} vs {dtm_array.shape}")
    return np.nan_to_num(dsm_array.astype("float32") - dtm_array.astype("float32"))


def extract_building_footprints(
    ndsm, transform=None, height_threshold_m: float | None = None
) -> list[ExtractedStructure]:
    """
    Thresholds nDSM, finds connected components with OpenCV, and traces contours
    to produce vector building footprints with height stats.
    """
    import numpy as np
    import cv2

    threshold = height_threshold_m or settings.NDSM_HEIGHT_THRESHOLD_M
    mask = (ndsm > threshold).astype("uint8") * 255

    # Morphological cleanup: close small gaps, remove speckle noise
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

    structures: list[ExtractedStructure] = []
    for label_id in range(1, num_labels):  # skip background label 0
        area_px = stats[label_id, cv2.CC_STAT_AREA]
        if area_px < 4:  # drop 1-2px noise specks
            continue

        component_mask = (labels == label_id).astype("uint8")
        contours, _ = cv2.findContours(component_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue
        contour = max(contours, key=cv2.contourArea)
        pixel_ring = contour.reshape(-1, 2).tolist()  # [[col,row], ...]

        heights = ndsm[labels == label_id]
        cx_px, cy_px = centroids[label_id]

        if transform is not None:
            ring_geo = [list(transform * (px, py)) for px, py in pixel_ring]
            cx, cy = transform * (cx_px, cy_px)
        else:
            ring_geo = [[float(px), float(py)] for px, py in pixel_ring]
            cx, cy = float(cx_px), float(cy_px)

        if ring_geo[0] != ring_geo[-1]:
            ring_geo.append(ring_geo[0])

        structures.append(
            ExtractedStructure(
                polygon=ring_geo,
                height_max=float(heights.max()),
                height_mean=float(heights.mean()),
                area=float(area_px),
                centroid=(cx, cy),
            )
        )
    return structures


def simplify_parcel_boundary(coords: list[list[float]], tolerance: float = 0.00002) -> list[list[float]]:
    """Parcel Cleanup: Douglas-Peucker simplification via shapely, small tolerance
    (~2m at equator) so we round noisy digitisation without eating real corners."""
    try:
        from shapely.geometry import Polygon, mapping
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("shapely required for parcel simplification") from exc

    poly = Polygon(coords).simplify(tolerance, preserve_topology=True)
    return list(mapping(poly)["coordinates"][0])
