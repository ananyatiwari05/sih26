import React, { useState } from 'react';
import 'leaflet/dist/leaflet.css';
import Header from './components/Header';
import MapCanvas from './components/MapCanvas';
import EvidenceCasePanel from './components/EvidenceCasePanel';
import LedgerViewer from './components/LedgerViewer';
import TimelineSlider from './components/TimelineSlider';
import LayerControls from './components/LayerControls';
import ExportModal from './components/ExportModal';
import { Database, FileDown } from 'lucide-react';

function App() {
  const [selectedFeature, setSelectedFeature] = useState(null);
  const [isLedgerOpen, setIsLedgerOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);
  const [activeLayer, setActiveLayer] = useState('cartodb');

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-slate-950 font-sans text-slate-100">
      <Header />
      
      <LayerControls activeLayer={activeLayer} setActiveLayer={setActiveLayer} />

      <MapCanvas 
        onFeatureSelect={setSelectedFeature} 
        selectedFeature={selectedFeature} 
        activeLayer={activeLayer}
      />

      <EvidenceCasePanel 
        selectedFeature={selectedFeature} 
        onClose={() => setSelectedFeature(null)} 
      />

      <TimelineSlider />
      
      <LedgerViewer 
        isOpen={isLedgerOpen} 
        onClose={() => setIsLedgerOpen(false)} 
      />

      <ExportModal 
        isOpen={isExportOpen} 
        onClose={() => setIsExportOpen(false)} 
        selectedFeature={selectedFeature}
      />

      {/* Floating Action Buttons for Global Tools */}
      <div className="absolute bottom-6 right-6 z-40 flex flex-col gap-3 pointer-events-auto">
        <button 
          onClick={() => setIsLedgerOpen(!isLedgerOpen)}
          className={`p-3 rounded-full shadow-2xl transition-all ${
            isLedgerOpen ? 'bg-blue-600 text-white' : 'bg-slate-800/90 text-blue-400 hover:bg-slate-700 hover:text-blue-300 border border-slate-600'
          }`}
          title="Immutable Trust Ledger"
        >
          <Database className="w-5 h-5" />
        </button>

        {selectedFeature?.properties?.type === 'VERIFIED' && (
          <button 
            onClick={() => setIsExportOpen(true)}
            className="p-3 rounded-full shadow-2xl bg-emerald-600 text-white hover:bg-emerald-500 transition-all border border-emerald-400/50"
            title="Export Sampatti Patrak"
          >
            <FileDown className="w-5 h-5" />
          </button>
        )}
      </div>

    </div>
  );
}

export default App;
