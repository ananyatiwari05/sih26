"""
Module F: Synthetic Dataset & Conflict Injection Generator.

Generates `SYNTHETIC_PARCEL_COUNT` (default 400) parcels over a bounding box
around a center point, and deterministically plants `SYNTHETIC_ANOMALY_COUNT`
(default 40) anomalies spread across all 6 classes. This is the primary
hardcoded dataset provider for offline hackathon demos (`DATA_BACKEND=memory`)
and is written to be a drop-in structural match for the frontend's own
`nazar-frontend/src/data/mockData.js` (same properties, same GeoJSON shape),
just generated server-side and served over `/api/v1/map/layers`.

Run standalone:
    python -m app.data.inject_conflicts --out synthetic_dataset.json
"""
from __future__ import annotations
import argparse
import json
import random
from dataclasses import asdict

from app.config import settings
from app.ledger.hash_chain import HashChain
from app.schemas.anomaly import AnomalyClass, ANOMALY_COLOR_HEX

OWNER_FIRST_NAMES = ["Ramesh", "Sunita", "Vikram", "Pooja", "Arjun", "Kavita", "Suresh", "Meena", "Anil", "Geeta"]
VILLAGES = ["Ramgarh", "Sultanpur", "Chandpur", "Devipura", "Nangla", "Barwala"]


def _polygon(base_lat: float, base_lng: float, size: float = 0.0005) -> list[list[float]]:
    return [
        [base_lng, base_lat],
        [base_lng + size, base_lat],
        [base_lng + size, base_lat + size],
        [base_lng, base_lat + size],
        [base_lng, base_lat],
    ]


def _drift_polygon(base_lat: float, base_lng: float, size: float = 0.0005) -> list[list[float]]:
    """A polygon deliberately offset from `_polygon` at the same base point, to
    represent the physically-surveyed footprint diverging from the recorded one."""
    return [
        [base_lng, base_lat],
        [base_lng + size * 1.2, base_lat - size * 0.2],
        [base_lng + size, base_lat + size],
        [base_lng - size * 0.1, base_lat + size * 0.9],
        [base_lng, base_lat],
    ]


def _grid_position(i: int, rng: random.Random, center_lat: float, center_lng: float) -> tuple[float, float]:
    """Spreads parcels over a roughly 1.5km x 1.5km area in a jittered grid."""
    cols = 20
    row, col = divmod(i, cols)
    lat = center_lat + (row - 10) * 0.0012 + rng.uniform(-0.0002, 0.0002)
    lng = center_lng + (col - 10) * 0.0012 + rng.uniform(-0.0002, 0.0002)
    return lat, lng


def _elevation_profile(peak_height: float) -> list[dict]:
    """Synthetic nDSM cross-section for the Evidence Case panel's height chart."""
    return [
        {"distance": 0, "ground": 0.0, "structure": 0.0},
        {"distance": 2, "ground": 0.1, "structure": round(peak_height * 0.1, 2)},
        {"distance": 4, "ground": 0.2, "structure": round(peak_height, 2)},
        {"distance": 6, "ground": 0.1, "structure": round(peak_height * 1.02, 2)},
        {"distance": 8, "ground": 0.1, "structure": round(peak_height * 0.98, 2)},
        {"distance": 10, "ground": 0.2, "structure": round(peak_height * 0.05, 2)},
        {"distance": 12, "ground": 0.0, "structure": 0.0},
    ]


def generate_dataset(
    parcel_count: int | None = None,
    anomaly_count: int | None = None,
    seed: int | None = None,
    center_lat: float | None = None,
    center_lng: float | None = None,
) -> dict:
    parcel_count = parcel_count or settings.SYNTHETIC_PARCEL_COUNT
    anomaly_count = anomaly_count or settings.SYNTHETIC_ANOMALY_COUNT
    seed = seed if seed is not None else settings.SYNTHETIC_SEED
    center_lat = center_lat or settings.SYNTHETIC_CENTER_LAT
    center_lng = center_lng or settings.SYNTHETIC_CENTER_LNG

    rng = random.Random(seed)

    anomaly_classes = [
        AnomalyClass.GHOST_STRUCTURE,
        AnomalyClass.PHANTOM_RECORD,
        AnomalyClass.BOUNDARY_DRIFT,
        AnomalyClass.ATTRIBUTE_MISMATCH,
        AnomalyClass.DUPLICATE_IDENTITY,
        AnomalyClass.TEMPORAL_GHOST,
    ]
    # Spread anomaly_count as evenly as possible across the 6 classes.
    per_class = anomaly_count // len(anomaly_classes)
    remainder = anomaly_count - per_class * len(anomaly_classes)
    class_quota: dict[AnomalyClass, int] = {c: per_class for c in anomaly_classes}
    for c in anomaly_classes[:remainder]:
        class_quota[c] += 1

    anomaly_slots = rng.sample(range(parcel_count), anomaly_count)
    slot_to_class: dict[int, AnomalyClass] = {}
    slot_pool = list(anomaly_slots)
    rng.shuffle(slot_pool)
    for cls, quota in class_quota.items():
        for _ in range(quota):
            slot_to_class[slot_pool.pop()] = cls

    features = []
    elevation_profiles: dict[str, list[dict]] = {}

    for i in range(parcel_count):
        lat, lng = _grid_position(i, rng, center_lat, center_lng)
        cls = slot_to_class.get(i, AnomalyClass.VERIFIED)
        survey_year = rng.choice([2023, 2024, 2025, 2026])
        area = round(rng.uniform(80, 600), 1)
        parcel_id_base = f"{cls.value}-{100 + i}"

        props: dict = {
            "id": parcel_id_base,
            "type": cls.value,
            "color": ANOMALY_COLOR_HEX[cls],
            "surveyYear": survey_year,
            "area": area,
        }

        if cls == AnomalyClass.GHOST_STRUCTURE:
            height = round(rng.uniform(3.0, 8.5), 1)
            props.update({
                "description": "Physical structure found via Drone nDSM, missing in official Cadastral Record.",
                "confidence": round(rng.uniform(90, 99), 1),
                "height": height,
                "status": "DISPUTED",
            })
            elevation_profiles[parcel_id_base] = _elevation_profile(height)
            geometry = {"type": "Polygon", "coordinates": [_polygon(lat, lng)]}

        elif cls == AnomalyClass.PHANTOM_RECORD:
            props.update({
                "description": "Title exists in official registry, but drone imagery shows empty land.",
                "confidence": round(rng.uniform(80, 93), 1),
                "status": "DISPUTED",
            })
            geometry = {"type": "Polygon", "coordinates": [_polygon(lat, lng, 0.0008)]}

        elif cls == AnomalyClass.BOUNDARY_DRIFT:
            drift_margin = round(rng.uniform(1.0, 3.0), 1)
            props.update({
                "description": "Physical surveyed boundary diverges from official cadastral coordinates.",
                "confidence": round(rng.uniform(85, 95), 1),
                "driftMargin": drift_margin,
                "status": "ANOMALY",
            })
            elevation_profiles[parcel_id_base] = _elevation_profile(1.5)
            geometry = {"type": "Polygon", "coordinates": [_drift_polygon(lat, lng)]}

        elif cls == AnomalyClass.ATTRIBUTE_MISMATCH:
            conflict_fields = rng.sample(["owner", "landUse", "areaRatio"], k=rng.choice([1, 2]))
            props.update({
                "description": f"Geometry matches, but {', '.join(conflict_fields)} conflict between revenue and GIS layers.",
                "confidence": round(rng.uniform(78, 90), 1),
                "conflictFields": conflict_fields,
                "recordedOwner": f"{rng.choice(OWNER_FIRST_NAMES)} (Revenue)",
                "surveyedOwner": f"{rng.choice(OWNER_FIRST_NAMES)} (GIS)",
                "status": "ANOMALY",
            })
            geometry = {"type": "Polygon", "coordinates": [_polygon(lat, lng, 0.0006)]}

        elif cls == AnomalyClass.DUPLICATE_IDENTITY:
            dup_ids = [f"REC-{rng.randint(5000,5999)}", f"REC-{rng.randint(6000,6999)}"]
            props.update({
                "description": f"{len(dup_ids)} conflicting record IDs map to the same physical parcel.",
                "confidence": round(rng.uniform(88, 97), 1),
                "duplicateIds": dup_ids,
                "status": "ANOMALY",
            })
            geometry = {"type": "Polygon", "coordinates": [_polygon(lat, lng, 0.0007)]}

        elif cls == AnomalyClass.TEMPORAL_GHOST:
            epochs = ["2021", "2023", "2025", "2026"]
            presence = {e: rng.choice([True, False]) for e in epochs}
            # force at least 2 flips so it's a genuine temporal ghost
            vals = list(presence.values())
            if sum(1 for i in range(1, len(vals)) if vals[i] != vals[i - 1]) < 2:
                presence = {e: bool(i % 2) for i, e in enumerate(epochs)}
            props.update({
                "description": "Structure appears, disappears and reappears across historical survey epochs.",
                "confidence": round(rng.uniform(82, 94), 1),
                "epochPresence": presence,
                "status": "ANOMALY",
            })
            geometry = {"type": "Polygon", "coordinates": [_polygon(lat, lng, 0.0005)]}

        else:  # VERIFIED
            props.update({
                "description": "Ground truth aligns with official SVAMITVA records.",
                "confidence": round(rng.uniform(96, 99.5), 1),
                "owner": f"{rng.choice(OWNER_FIRST_NAMES)} ({rng.choice(VILLAGES)})",
                "status": "SYNC_READY",
            })
            geometry = {"type": "Polygon", "coordinates": [_polygon(lat, lng, 0.0006)]}

        features.append({"type": "Feature", "properties": props, "geometry": geometry})

    geojson = {"type": "FeatureCollection", "features": features}

    # Build a plausible initial ledger: a DRONE_SYNC batch event, then one
    # officer action per anomaly class actually present in this run.
    chain = HashChain()
    chain.append("SYS-AUTO", "DRONE_SYNC", "BATCH-A", notes=f"Ingested {parcel_count} parcels")
    officer_ids = ["OFF-8472", "OFF-3391", "OFF-5510"]
    anomaly_features = [f for f in features if f["properties"]["status"] != "SYNC_READY"]
    for feat in rng.sample(anomaly_features, k=min(4, len(anomaly_features))):
        action = rng.choice(["FLAG_" + feat["properties"]["type"], "UPDATE_BOUNDARY", "VERIFY_PARCEL"])
        chain.append(rng.choice(officer_ids), action, feat["properties"]["id"])

    counts = {c.value: 0 for c in anomaly_classes}
    for f in features:
        t = f["properties"]["type"]
        if t in counts:
            counts[t] += 1

    return {
        "geoJsonData": geojson,
        "elevationProfiles": elevation_profiles,
        "initialLedgerData": chain.to_dict_list(),
        "summary": {
            "totalScanned": parcel_count,
            "anomalyBreakdown": counts,
            "verifiedCount": parcel_count - anomaly_count,
        },
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="Generate the NAZAR 2.0 synthetic demo dataset (Module F).")
    parser.add_argument("--out", default="synthetic_dataset.json")
    parser.add_argument("--parcels", type=int, default=None)
    parser.add_argument("--anomalies", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    dataset = generate_dataset(parcel_count=args.parcels, anomaly_count=args.anomalies, seed=args.seed)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(dataset, fh, indent=2)
    print(f"Wrote {len(dataset['geoJsonData']['features'])} features -> {args.out}")
    print("Anomaly breakdown:", dataset["summary"]["anomalyBreakdown"])


if __name__ == "__main__":
    _main()
