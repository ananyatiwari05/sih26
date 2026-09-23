import React from 'react';
import { Layers } from 'lucide-react';

const LayerControls = ({ activeLayer, setActiveLayer }) => {
  return (
    <div className="absolute top-20 left-4 z-40 bg-black border border-white p-2 pointer-events-auto flex flex-col gap-2 font-mono shadow-[4px_4px_0px_white] rounded-none">
      <div className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest text-center pb-2 border-b border-zinc-800">
        TILE_SRC
      </div>
      
      <button 
        onClick={() => setActiveLayer('cartodb')}
        className={`flex items-center gap-2 px-3 py-2 rounded-none transition-colors border ${
          activeLayer === 'cartodb' 
            ? 'bg-white text-black border-white' 
            : 'hover:bg-zinc-900 text-zinc-400 border-transparent hover:border-zinc-700'
        }`}
      >
        <span className="text-xs font-bold uppercase tracking-widest">OSM_BW_FILTER</span>
      </button>
    </div>
  );
};

export default LayerControls;
