import React from 'react';
import { Map, Layers } from 'lucide-react';

const LayerControls = ({ activeLayer, setActiveLayer }) => {
  return (
    <div className="absolute top-24 left-4 z-40 bg-slate-900/85 backdrop-blur-md border border-slate-700/60 rounded-lg shadow-2xl p-2 pointer-events-auto flex flex-col gap-2">
      <div className="text-[10px] text-slate-400 uppercase font-bold tracking-widest text-center pb-2 border-b border-slate-700/60">
        Base Map
      </div>
      
      <button 
        onClick={() => setActiveLayer('cartodb')}
        className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${
          activeLayer === 'cartodb' 
            ? 'bg-emerald-900/40 text-emerald-400 border border-emerald-500/30' 
            : 'hover:bg-slate-800 text-slate-300 border border-transparent'
        }`}
      >
        <Map className="w-4 h-4" />
        <span className="text-xs font-semibold">Dark Matter</span>
      </button>

      <button 
        onClick={() => setActiveLayer('osm')}
        className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${
          activeLayer === 'osm' 
            ? 'bg-emerald-900/40 text-emerald-400 border border-emerald-500/30' 
            : 'hover:bg-slate-800 text-slate-300 border border-transparent'
        }`}
      >
        <Layers className="w-4 h-4" />
        <span className="text-xs font-semibold">OSM Standard</span>
      </button>
    </div>
  );
};

export default LayerControls;
