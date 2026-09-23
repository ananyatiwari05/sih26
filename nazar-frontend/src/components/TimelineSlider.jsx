import React, { useState } from 'react';
import { History, Play, Pause } from 'lucide-react';

const TimelineSlider = () => {
  const years = [2021, 2023, 2025, 2026];
  const [currentYear, setCurrentYear] = useState(2026);
  const [isPlaying, setIsPlaying] = useState(false);

  // Note: Actual filtering of map data would be lifted up to App.jsx in a real app,
  // but for the visual component we just need the UI state.

  const handleSliderChange = (e) => {
    setCurrentYear(parseInt(e.target.value));
  };

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-40 bg-slate-900/85 backdrop-blur-md border border-slate-700/60 rounded-xl shadow-2xl px-6 py-4 flex items-center gap-6 pointer-events-auto w-[600px] max-w-[90vw]">
      
      <div className="flex flex-col items-center gap-1">
        <button 
          onClick={() => setIsPlaying(!isPlaying)}
          className="p-2 bg-blue-900/40 text-blue-400 rounded-full hover:bg-blue-800/60 transition-colors border border-blue-500/30"
        >
          {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
        </button>
        <span className="text-[10px] text-slate-400 uppercase font-bold tracking-widest mt-1">Scrub</span>
      </div>

      <div className="flex-1">
        <div className="flex justify-between mb-2">
          <div className="flex items-center gap-2 text-slate-300">
            <History className="w-4 h-4" />
            <span className="text-xs font-mono font-bold uppercase tracking-wider">Epoch Timeline</span>
          </div>
          <div className="text-emerald-400 font-mono font-bold text-sm bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/30">
            {currentYear} Survey
          </div>
        </div>
        
        <input 
          type="range" 
          min={2021} 
          max={2026} 
          step={1}
          value={currentYear}
          onChange={handleSliderChange}
          className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500 outline-none"
        />
        
        <div className="flex justify-between mt-2 px-1 text-[10px] font-mono text-slate-500">
          <span>2021 (Base)</span>
          <span>2023 (Phase I)</span>
          <span>2025 (Phase II)</span>
          <span className="text-slate-300 font-bold">2026 (Live)</span>
        </div>
      </div>
    </div>
  );
};

export default TimelineSlider;
