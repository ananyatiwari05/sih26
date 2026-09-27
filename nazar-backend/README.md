# NAZAR 2.0 — Ground Truth Engine — Backend

FastAPI backend + geospatial ML pipeline for the NAZAR 2.0 (SIH 2026) frontend
(`nazar-frontend`, React + Leaflet). Implements the flowchart in `Solution Setup`:

```
Multi-Source Input -> Data Standardization -> CRS Detect/Transform/Validate
  -> Topology Correction -> {Building Extraction, Parcel Cleanup}
  -> Spatial Matching Engine -> Confidence & Anomaly Engine (6 classes + Trust Ledger)
```

## 1. Quick start (offline hackathon demo mode)

Demo mode needs **no PostGIS, no drone data** — it runs entirely on the synthetic
dataset generator (Module F) held in memory, which is exactly what the frontend's
`mockData.js` expects.

```bash
cd nazar-backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for Swagger UI.
Point the frontend at it: in `nazar-frontend`, set `VITE_API_BASE_URL=http://localhost:8000/api/v1`
and swap `mockData.js` imports for `fetch('/api/v1/map/layers')` calls (see
`FRONTEND_INTEGRATION.md`).

On boot (`DATA_BACKEND=memory`, the default) the app calls
`app/data/inject_conflicts.py` to generate 400 synthetic parcels with ~40 planted
anomalies across all 6 classes and a genuine SHA-256 ledger chain — no external
services required.

## 2. Full pipeline mode (real drone/cadastral data + PostGIS)

```bash
docker compose up -d db            # Postgres + PostGIS
cp .env.example .env               # set DATA_BACKEND=postgis, fill DB_* vars
alembic upgrade head                # create tables (see app/db/models.py)
uvicorn app.main:app --reload --port 8000
```

Then drive the flowchart stage by stage via the API (or let
`pipeline/pipeline_runner.py` chain them for you):

1. `POST /api/v1/ingest` — upload Cadastral GeoJSON/SHP, Drone DSM/DTM GeoTIFF, Revenue CSV
2. `POST /api/v1/standardize` — CRS detect → reproject → validate geometry → fix topology
3. `POST /api/v1/extract` — compute nDSM, extract building footprints, clean parcels
4. `POST /api/v1/spatial-match` — IoU / centroid / edge / attribute composite matching
5. `POST /api/v1/classify` — assign one of the 6 anomaly classes + confidence + rationale
6. `GET /api/v1/map/layers`, `GET /api/v1/anomalies/{id}` — serve the map/Evidence Case UI
7. `POST /api/v1/anomalies/{id}/action` — officer accepts/edits/rejects → ledger block appended
8. `GET /api/v1/ledger/verify` — validate the hash chain, detect tampering

## 3. Folder structure

See `STRUCTURE.md` for the annotated tree.

## 4. Anomaly taxonomy (Module D)

| Class | Color | Code |
|---|---|---|
| Ghost Structure | Red `#EF4444` | `GHOST_STRUCTURE` |
| Phantom Record | Orange `#F97316` | `PHANTOM_RECORD` |
| Boundary Drift | Yellow `#EAB308` | `BOUNDARY_DRIFT` |
| Attribute Mismatch | Blue `#3B82F6` | `ATTRIBUTE_MISMATCH` |
| Duplicate Identity | Purple `#A855F7` | `DUPLICATE_IDENTITY` |
| Temporal Ghost | Black `#18181B` | `TEMPORAL_GHOST` |
| (clean parcel) | — | `VERIFIED` |

## 5. Tests

```bash
pytest tests/ -v
```
