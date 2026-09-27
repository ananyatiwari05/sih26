import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polygon, useMap } from 'react-leaflet';

const MapController = ({ selectedFeature }) => {
  const map = useMap();
  
  useEffect(() => {
    if (selectedFeature && selectedFeature.geometry && selectedFeature.geometry.coordinates) {
      const coords = selectedFeature.geometry.coordinates[0];
      const lats = coords.map(c => c[1]);
      const lngs = coords.map(c => c[0]);
      const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
      const centerLng = (Math.min(...lngs) + Math.max(...lngs)) / 2;
      
      map.flyTo([centerLat, centerLng], 18, { duration: 1.5 });
    }
  }, [selectedFeature, map]);

  return null;
};

const MapCanvas = ({ onFeatureSelect, selectedFeature, currentEpoch }) => {
  const center = [23.2599, 77.4126];
  const [geoJsonData, setGeoJsonData] = useState({ features: [] });

  const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

  useEffect(() => {
    let url = `${API_URL}/map/layers`;
    if (currentEpoch) url += `?epoch=${currentEpoch}`;
    fetch(url)
      .then(res => res.json())
      .then(data => setGeoJsonData(data.all || { features: [] }))
      .catch(err => console.error("Failed to load map layers:", err));
  }, [currentEpoch]);

  const getStyleForFeature = (feature) => {
    const isSelected = selectedFeature?.properties.id === feature.properties.id;
    const selectionWeightOffset = isSelected ? 3 : 0;
    
    // Default Anomalous style (red/warm shaded)
    let baseColor = '#EF4444'; // RED fallback
    let dash = "4 4";
    let fillOpacity = 0.25;

    switch (feature.properties.type) {
      case 'RED':
      case 'GHOST_STRUCTURE':
        baseColor = '#EF4444'; // Red
        break;
      case 'ORANGE':
      case 'PHANTOM_RECORD':
        baseColor = '#F97316'; // Orange
        break;
      case 'YELLOW':
      case 'BOUNDARY_DRIFT':
        baseColor = '#EAB308'; // Yellow
        break;
      case 'BLUE':
        baseColor = '#3B82F6'; // Blue
        break;
      case 'PURPLE':
        baseColor = '#A855F7'; // Purple
        break;
      case 'BLACK':
        baseColor = '#18181B'; // Black
        dash = "0"; // solid glowing outline
        break;
      case 'VERIFIED':
        return { fillColor: "#ffffff", fillOpacity: 0.05, color: "#52525B", weight: 1 + selectionWeightOffset };
      default:
        break;
    }

    return { 
      fillColor: baseColor, 
      fillOpacity: fillOpacity, 
      color: baseColor, 
      weight: 2 + selectionWeightOffset, 
      dashArray: dash 
    };
  };

  return (
    <div className="absolute inset-0 z-0 bg-black">
      <MapContainer 
        center={center} 
        zoom={16} 
        zoomControl={false}
        style={{ height: '100vh', width: '100vw' }}
      >
        <TileLayer 
          attribution="&copy; OpenStreetMap" 
          className="map-tiles-bw" 
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {geoJsonData.features.map((feature, idx) => {
          const positions = feature.geometry.coordinates[0].map(coord => [coord[1], coord[0]]);
          return (
            <Polygon
              key={idx}
              positions={positions}
              pathOptions={getStyleForFeature(feature)}
              eventHandlers={{
                click: () => onFeatureSelect(feature)
              }}
            />
          );
        })}

        <MapController selectedFeature={selectedFeature} />
      </MapContainer>
    </div>
  );
};

export default MapCanvas;
