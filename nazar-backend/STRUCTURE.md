nazar-backend/
├── README.md
├── STRUCTURE.md
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml                  # Postgres+PostGIS for full pipeline mode
├── pytest.ini
│
├── app/
│   ├── main.py                         # FastAPI app factory, CORS, startup seeds demo data
│   ├── config.py                       # Settings (env-driven): DATA_BACKEND, weights, thresholds
│   │
│   ├── db/
│   │   ├── session.py                  # SQLAlchemy engine/session (postgis mode)
│   │   ├── models.py                   # ORM: Parcel, Structure, Anomaly, LedgerBlock (GeoAlchemy2)
│   │   └── memory_store.py             # In-process store used in demo mode (dict-backed)
│   │
│   ├── schemas/
│   │   ├── geojson.py                  # Feature / FeatureCollection Pydantic models
│   │   ├── anomaly.py                  # AnomalyClass enum, EvidenceCase, ActionRequest
│   │   ├── ledger.py                   # LedgerBlockOut, LedgerVerifyResult
│   │   └── ingest.py                   # Upload manifests for Module A
│   │
│   ├── pipeline/                       # <-- the 6 flowchart stages, one module each
│   │   ├── ingestion.py                # Module A: multi-source handlers
│   │   ├── standardization.py          # Module A: CRS detect/transform, geometry/topology fix
│   │   ├── extraction.py               # Module B: nDSM = DSM-DTM, OpenCV building extraction
│   │   ├── spatial_matching.py         # Module C: IoU + centroid + edge + attribute score
│   │   ├── anomaly_classifier.py       # Module D: 6-class rules engine + rationale text
│   │   ├── trust_engine.py             # Module E: Bayesian per-source trust weighting
│   │   └── pipeline_runner.py          # Orchestrates stages 1->6 end to end
│   │
│   ├── ledger/
│   │   └── hash_chain.py               # Module E: SHA-256 append-only chain + verify()
│   │
│   ├── services/
│   │   ├── map_service.py              # Builds /map/layers GeoJSON from store
│   │   ├── anomaly_service.py          # Builds Evidence Case payload + applies actions
│   │   └── ledger_service.py           # Append/list/verify wrapper over hash_chain
│   │
│   ├── api/v1/
│   │   ├── router.py                   # Mounts all endpoint routers under /api/v1
│   │   └── endpoints/
│   │       ├── ingest.py               # POST /ingest
│   │       ├── standardize.py          # POST /standardize
│   │       ├── extract.py              # POST /extract
│   │       ├── spatial_match.py        # POST /spatial-match
│   │       ├── classify.py             # POST /classify
│   │       ├── map_layers.py           # GET  /map/layers
│   │       ├── anomalies.py            # GET  /anomalies/{id}, POST /anomalies/{id}/action
│   │       ├── ledger.py               # GET  /ledger, GET /ledger/verify
│   │       └── synthetic.py            # POST /synthetic/generate (re-run Module F)
│   │
│   ├── data/
│   │   └── inject_conflicts.py         # Module F: 400 parcels + ~40 planted anomalies
│   │
│   └── utils/
│       └── geometry_utils.py           # IoU, centroid distance, polygon helpers (shapely)
│
├── scripts/
│   ├── run_dev.sh                      # uvicorn launcher
│   └── generate_synthetic_dataset.py   # CLI: python scripts/generate_synthetic_dataset.py
│
└── tests/
    ├── test_ledger.py                  # hash-chain integrity + tamper detection
    ├── test_classifier.py              # each of the 6 anomaly rules
    └── test_spatial_matching.py        # composite score math
