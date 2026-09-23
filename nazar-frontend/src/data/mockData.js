// Base coordinates: 28.5355, 77.3910 (Noida/Rural UP area)
const generatePolygon = (baseLat, baseLng, size = 0.0005) => {
  return [
    [baseLng, baseLat],
    [baseLng + size, baseLat],
    [baseLng + size, baseLat + size],
    [baseLng, baseLat + size],
    [baseLng, baseLat]
  ];
};

const generateDriftPolygon = (baseLat, baseLng, size = 0.0005) => {
  return [
    [baseLng, baseLat],
    [baseLng + size * 1.2, baseLat - size * 0.2],
    [baseLng + size, baseLat + size],
    [baseLng - size * 0.1, baseLat + size * 0.9],
    [baseLng, baseLat]
  ];
};

// 5 Red Ghost Structures
const ghostStructures = Array.from({ length: 5 }).map((_, i) => ({
  type: "Feature",
  properties: {
    id: `GHOST-${100 + i}`,
    type: "GHOST_STRUCTURE",
    description: "Physical structure found via Drone nDSM, missing in official Cadastral Record.",
    confidence: 96 - i,
    height: (4.2 + (i * 1.1)).toFixed(1),
    area: Math.floor(120 + i * 25),
    surveyYear: 2024,
    status: "DISPUTED"
  },
  geometry: {
    type: "Polygon",
    coordinates: [generatePolygon(28.5355 + (i * 0.0015), 77.3910 + (i * 0.001))]
  }
}));

// 3 Orange Phantom Records
const phantomRecords = Array.from({ length: 3 }).map((_, i) => ({
  type: "Feature",
  properties: {
    id: `PHANTOM-${200 + i}`,
    type: "PHANTOM_RECORD",
    description: "Title exists in official registry, but drone imagery shows empty agricultural land.",
    confidence: 88 + i,
    area: Math.floor(400 + i * 50),
    surveyYear: 2021,
    status: "DISPUTED"
  },
  geometry: {
    type: "Polygon",
    coordinates: [generatePolygon(28.5330 - (i * 0.002), 77.3880 + (i * 0.0015), 0.0008)]
  }
}));

// 4 Yellow Boundary Drifts
const boundaryDrifts = Array.from({ length: 4 }).map((_, i) => ({
  type: "Feature",
  properties: {
    id: `DRIFT-${300 + i}`,
    type: "BOUNDARY_DRIFT",
    description: "Physical fenced boundary diverges from official coordinates by > 1.5 meters.",
    confidence: 92,
    driftMargin: (1.5 + (i * 0.4)).toFixed(1),
    surveyYear: 2023,
    status: "ANOMALY"
  },
  geometry: {
    type: "Polygon",
    coordinates: [generateDriftPolygon(28.5380 + (i * 0.001), 77.3940 - (i * 0.0012))]
  }
}));

// 10 Emerald Verified Parcels
const verifiedParcels = Array.from({ length: 10 }).map((_, i) => ({
  type: "Feature",
  properties: {
    id: `VERIFIED-${400 + i}`,
    type: "VERIFIED",
    description: "Ground truth perfectly aligns with SVAMITVA official records.",
    confidence: 99,
    area: Math.floor(200 + i * 40),
    owner: `Local Resident ${i + 1}`,
    surveyYear: 2025,
    status: "SYNC_READY"
  },
  geometry: {
    type: "Polygon",
    coordinates: [generatePolygon(28.5340 + (i%3 * 0.002), 77.3960 + (Math.floor(i/3) * 0.0015), 0.0006)]
  }
}));

export const geoJsonData = {
  type: "FeatureCollection",
  features: [
    ...ghostStructures,
    ...phantomRecords,
    ...boundaryDrifts,
    ...verifiedParcels
  ]
};

// Initial Immutable Ledger Hash Chain Data
export const initialLedgerData = [
  {
    block: 104,
    hash: "a4f8...9c3b",
    prevHash: "e2c4...7a1f",
    timestamp: "2026-09-21 14:32:00",
    officerId: "OFF-8472",
    action: "VERIFY_PARCEL",
    parcelId: "VERIFIED-400",
    tampered: false
  },
  {
    block: 103,
    hash: "e2c4...7a1f",
    prevHash: "9b1a...3f8d",
    timestamp: "2026-09-20 09:15:22",
    officerId: "OFF-8472",
    action: "FLAG_GHOST",
    parcelId: "GHOST-100",
    tampered: false
  },
  {
    block: 102,
    hash: "9b1a...3f8d",
    prevHash: "7f4c...2e5a",
    timestamp: "2026-09-18 16:45:10",
    officerId: "OFF-3391",
    action: "UPDATE_BOUNDARY",
    parcelId: "DRIFT-301",
    tampered: false
  },
  {
    block: 101,
    hash: "7f4c...2e5a",
    prevHash: "0000...0000",
    timestamp: "2026-09-15 11:20:05",
    officerId: "SYS-AUTO",
    action: "DRONE_SYNC",
    parcelId: "BATCH-A",
    tampered: false
  }
];

export const elevationChartData = [
  { distance: 0, ground: 0, structure: 0 },
  { distance: 2, ground: 0.1, structure: 0.1 },
  { distance: 4, ground: 0.2, structure: 4.2 },
  { distance: 6, ground: 0.1, structure: 4.3 },
  { distance: 8, ground: 0.1, structure: 4.2 },
  { distance: 10, ground: 0.2, structure: 0.2 },
  { distance: 12, ground: 0, structure: 0 },
];
