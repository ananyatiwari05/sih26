import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, useMap } from 'react-leaflet';
import { geoJsonData } from '../data/mockData';

const MapController = ({ selectedFeature }) => {
  const map = useMap();
  
  useEffect(() => {
    if (selectedFeature) {
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

const MapCanvas = ({ onFeatureSelect, selectedFeature }) => {
  const center = [28.5355, 77.3910];

  const getStyleForFeature = (feature) => {
    const isSelected = selectedFeature?.properties.id === feature.properties.id;
    
    // Base style modifier if selected (make it pop with thicker border)
    const selectionWeightOffset = isSelected ? 2 : 0;

    switch (feature.properties.type) {
      case 'GHOST_STRUCTURE':
        return { fillColor: "#ffffff", fillOpacity: 0.2, color: "#ffffff", weight: 2 + selectionWeightOffset, dashArray: "4 4" };
      case 'PHANTOM_RECORD':
        return { fillColor: "#000000", fillOpacity: 0.8, color: "#ffffff", weight: 1 + selectionWeightOffset, dashArray: "1 4" };
      case 'BOUNDARY_DRIFT':
        return { fillColor: "transparent", color: "#ffffff", weight: 3 + selectionWeightOffset, dashArray: "10 5" };
      case 'VERIFIED':
        return { fillColor: "#ffffff", fillOpacity: 0.05, color: "#52525B", weight: 1 + selectionWeightOffset };
      default:
        return { color: '#ffffff', fillColor: '#ffffff' };
    }
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
