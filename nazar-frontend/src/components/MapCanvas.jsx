import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, useMap } from 'react-leaflet';
import { geoJsonData } from '../data/mockData';

const MapController = ({ selectedFeature }) => {
  const map = useMap();
  
  useEffect(() => {
    if (selectedFeature) {
      const coords = selectedFeature.geometry.coordinates[0];
      // Basic center calculation
      const lats = coords.map(c => c[1]);
      const lngs = coords.map(c => c[0]);
      const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
      const centerLng = (Math.min(...lngs) + Math.max(...lngs)) / 2;
      
      map.flyTo([centerLat, centerLng], 18, { duration: 1.5 });
    }
  }, [selectedFeature, map]);

  return null;
};

const MapCanvas = ({ onFeatureSelect, selectedFeature, activeLayer }) => {
  const center = [28.5355, 77.3910];

  const getStyleForFeature = (feature) => {
    const isSelected = selectedFeature?.properties.id === feature.properties.id;
    const baseStyle = { weight: 2, fillOpacity: 0.35 };

    switch (feature.properties.type) {
      case 'GHOST_STRUCTURE':
        return { ...baseStyle, color: '#DC2626', fillColor: '#EF4444', weight: isSelected ? 4 : 2 };
      case 'PHANTOM_RECORD':
        return { ...baseStyle, color: '#D97706', fillColor: '#F59E0B', weight: isSelected ? 4 : 2 };
      case 'BOUNDARY_DRIFT':
        return { ...baseStyle, color: '#CA8A04', fillColor: '#EAB308', weight: isSelected ? 4 : 2 };
      case 'VERIFIED':
        return { color: '#10B981', fillColor: '#10B981', fillOpacity: 0.05, weight: isSelected ? 3 : 1 };
      default:
        return { color: '#3388ff', fillColor: '#3388ff' };
    }
  };

  const tileUrls = {
    cartodb: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    osm: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
  };

  return (
    <div className="absolute inset-0 z-0 bg-[#020617]">
      <MapContainer 
        center={center} 
        zoom={16} 
        zoomControl={false}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url={tileUrls[activeLayer || 'cartodb']}
        />
        
        {geoJsonData.features.map((feature, idx) => {
          // Leaflet expects [lat, lng], GeoJSON is [lng, lat]
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
