import React, { useState } from 'react';
import { Square, SquareCheck } from 'lucide-react';

const TimelineSlider = () => {
  const years = [2021, 2023, 2025, 2026];
  const [currentYear, setCurrentYear] = useState(2026);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleSliderChange = (e) => {
    setCurrentYear(parseInt(e.target.value));
  };

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-40 bg-black border border-white p-4 flex flex-col gap-3 pointer-events-auto w-[600px] max-w-[90vw] shadow-[4px_4px_0px_white] rounded-none font-mono">
      
      <div className="flex justify-between items-end border-b border-zinc-800 pb-2">
        <div className="flex items-center gap-3 text-white">
          <button 
            onClick={() => setIsPlaying(!isPlaying)}
            className="border border-white hover:bg-white hover:text-black transition-colors p-1"
          >
            {isPlaying ? <SquareCheck className="w-4 h-4 fill-current" /> : <Square className="w-4 h-4" />}
          </button>
          <span className="text-xs font-bold uppercase tracking-widest">TEMPORAL_SCRUB</span>
        </div>
        <div className="bg-white text-black font-bold text-xs px-2 py-0.5 uppercase">
          EPOCH: {currentYear}
        </div>
      </div>

      <div className="relative pt-4 pb-2">
        {/* Brutalist Custom Slider Styling */}
        <input 
          type="range" 
          min={2021} 
          max={2026} 
          step={1}
          value={currentYear}
          onChange={handleSliderChange}
          className="w-full appearance-none bg-transparent focus:outline-none z-10 relative cursor-pointer brutal-slider"
        />
        
        {/* The Track (1px white line) */}
        <div className="absolute top-[21px] left-0 right-0 h-[1px] bg-white z-0"></div>

        <div className="flex justify-between mt-4 px-1 text-[9px] uppercase tracking-widest text-zinc-500">
          <span className={currentYear === 2021 ? 'text-white font-bold' : ''}>2021_BASE</span>
          <span className={currentYear === 2023 ? 'text-white font-bold' : ''}>2023_PH1</span>
          <span className={currentYear === 2025 ? 'text-white font-bold' : ''}>2025_PH2</span>
          <span className={currentYear === 2026 ? 'text-white font-bold' : ''}>2026_LIVE</span>
        </div>
      </div>
    </div>
  );
};

export default TimelineSlider;
