# Wiring `nazar-frontend` to this backend

The frontend currently reads two static files:
`src/data/mockData.js` → `geoJsonData`, `initialLedgerData`, `elevationChartData`.

To go live, replace those imports with fetches against this API. Nothing else
in the components needs to change — the shapes match.

## 1. `MapCanvas.jsx`

```diff
- import { geoJsonData } from '../data/mockData';
+ import { useEffect, useState } from 'react';
+ const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

  const MapCanvas = ({ onFeatureSelect, selectedFeature }) => {
+   const [geoJsonData, setGeoJsonData] = useState({ type: 'FeatureCollection', features: [] });
+   useEffect(() => {
+     fetch(`${API_BASE}/map/layers`)
+       .then(r => r.json())
+       .then(data => setGeoJsonData(data.all));
+   }, []);
```

Add a style branch for the two new classes the backend can emit that the
original mock didn't have:

```js
case 'ATTRIBUTE_MISMATCH':
  return { fillColor: "#3B82F6", fillOpacity: 0.25, color: "#3B82F6", weight: 2 };
case 'DUPLICATE_IDENTITY':
  return { fillColor: "#A855F7", fillOpacity: 0.25, color: "#A855F7", weight: 2, dashArray: "2 6" };
case 'TEMPORAL_GHOST':
  return { fillColor: "#18181B", fillOpacity: 0.6, color: "#ffffff", weight: 2, dashArray: "1 3" };
```

## 2. `EvidenceCasePanel.jsx`

On `selectedFeature` change, fetch the full case instead of relying only on the
GeoJSON properties (this also gets you the freshly computed `rationale` and,
for Ghost/Drift parcels, an `elevationProfile` array to feed the existing
`elevationChartData`-shaped `<AreaChart>`):

```js
useEffect(() => {
  if (!selectedFeature) return;
  fetch(`${API_BASE}/anomalies/${selectedFeature.properties.id}`)
    .then(r => r.json())
    .then(setEvidenceCase);
}, [selectedFeature]);
```

Wire the Accept/Reject/Edit buttons to `POST /anomalies/{id}/action`:

```js
const act = (action) =>
  fetch(`${API_BASE}/anomalies/${properties.id}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, officerId: 'OFF-8472' }),
  }).then(r => r.json());

<button onClick={() => act('REJECT')}>REJECT</button>
<button onClick={() => act('ACCEPT')}>ACCEPT</button>
```

## 3. `LedgerViewer.jsx`

```diff
- import { initialLedgerData } from '../data/mockData';
+ const [ledger, setLedger] = useState([]);
+ useEffect(() => { fetch(`${API_BASE}/ledger`).then(r => r.json()).then(setLedger); }, [isOpen]);
```

The "sudo inject_fault" button already calls a local `simulateTampering(idx)` —
point it at the real endpoint instead so the break is genuine, not simulated
client-side:

```js
const simulateTampering = (block) =>
  fetch(`${API_BASE}/ledger/simulate-tamper/${block}`, { method: 'POST' })
    .then(r => r.json())
    .then(() => fetch(`${API_BASE}/ledger`).then(r => r.json()).then(setLedger));
```

## 4. Header metrics ticker

`Header.jsx` hardcodes `SCANNED / GHOSTS / PHANTOMS / DRIFTS`. Source these from
`GET /map/layers` → `summary.anomalyBreakdown` and `summary.totalScanned`
instead.

## 5. Env

Add to `nazar-frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

And make sure the backend's `ALLOWED_ORIGINS` in `.env` includes the Vite dev
server origin (`http://localhost:5173` is already the default).
