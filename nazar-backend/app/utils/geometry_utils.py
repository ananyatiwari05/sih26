"""
Pure-geometry helpers for Module C (Spatial Matching Engine). Uses shapely when
available; falls back to lightweight pure-Python implementations so the demo
(`DATA_BACKEND=memory`) never hard-fails on a missing binary wheel.
"""
from __future__ import annotations
import math

try:
    from shapely.geometry import shape, Polygon
    from shapely.ops import unary_union
    _HAS_SHAPELY = True
except ImportError:  # pragma: no cover
    _HAS_SHAPELY = False


def _ring_area(coords: list[list[float]]) -> float:
    """Shoelace formula fallback (planar, fine for small parcel-scale polygons)."""
    area = 0.0
    n = len(coords)
    for i in range(n - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i + 1]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def centroid_of(coords: list[list[float]]) -> tuple[float, float]:
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def haversine_m(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Great-circle distance in meters between two (lng, lat) points."""
    lng1, lat1 = p1
    lng2, lat2 = p2
    r = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def _bounds(coords: list[list[float]]) -> tuple[float, float, float, float]:
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return min(xs), min(ys), max(xs), max(ys)


def _bounds_overlap(coords_a: list[list[float]], coords_b: list[list[float]]) -> bool:
    ax0, ay0, ax1, ay1 = _bounds(coords_a)
    bx0, by0, bx1, by1 = _bounds(coords_b)
    return ax0 <= bx1 and bx0 <= ax1 and ay0 <= by1 and by0 <= ay1


def polygon_iou(coords_a: list[list[float]], coords_b: list[list[float]]) -> float:
    """Intersection-over-Union of two polygon rings (each a closed [ [lng,lat], ... ])."""
    if _HAS_SHAPELY:
        pa, pb = Polygon(coords_a), Polygon(coords_b)
        if not pa.is_valid:
            pa = pa.buffer(0)
        if not pb.is_valid:
            pb = pb.buffer(0)
        inter = pa.intersection(pb).area
        union = pa.union(pb).area
        return inter / union if union > 0 else 0.0
    # Fallback when shapely isn't installed: bounding boxes that don't even
    # overlap can never intersect, regardless of area ratio. When they do
    # overlap, fall back to a crude area-ratio proxy (good enough to rank
    # candidates; install shapely for a real intersection computation).
    if not _bounds_overlap(coords_a, coords_b):
        return 0.0
    area_a, area_b = _ring_area(coords_a), _ring_area(coords_b)
    smaller, larger = min(area_a, area_b), max(area_a, area_b)
    return smaller / larger if larger > 0 else 0.0


def centroid_proximity_score(coords_a: list[list[float]], coords_b: list[list[float]],
                              decay_m: float = 5.0) -> float:
    """1.0 at zero distance, exponential decay to ~0 by `decay_m` meters apart."""
    d = haversine_m(centroid_of(coords_a), centroid_of(coords_b))
    return math.exp(-d / decay_m)


def area_ratio_score(coords_a: list[list[float]], coords_b: list[list[float]]) -> float:
    """Ratio of smaller area to larger area (0..1)."""
    area_a = _ring_area(coords_a)
    area_b = _ring_area(coords_b)
    smaller, larger = min(area_a, area_b), max(area_a, area_b)
    return smaller / larger if larger > 0 else 0.0


def attribute_agreement_score(attrs_a: dict, attrs_b: dict, keys: list[str]) -> float:
    if not keys:
        return 1.0
    hits = sum(1 for k in keys if str(attrs_a.get(k)).strip().lower() == str(attrs_b.get(k)).strip().lower())
    return hits / len(keys)
