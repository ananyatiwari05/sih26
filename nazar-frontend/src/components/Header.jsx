import React from 'react';
import { ShieldCheck, Crosshair } from 'lucide-react';
import VoiceSearchBar from './VoiceSearchBar';

const Header = () => {
  return (
    <header className="absolute top-0 left-0 w-full z-50 pointer-events-none">
      <div className="bg-black border-b border-zinc-700 p-3 flex items-center justify-between pointer-events-auto shadow-[0px_4px_0px_rgba(255,255,255,1)]">
        
        {/* Branding & Badge */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <Crosshair className="w-5 h-5 text-white" />
            <div>
              <h1 className="text-lg font-bold tracking-widest text-white uppercase sans-serif leading-none">NAZAR</h1>
              <p className="text-[9px] text-zinc-400 uppercase tracking-widest font-mono mt-0.5">Ground Truth Engine</p>
            </div>
          </div>
          
          <div className="border border-zinc-600 px-2 py-1 flex items-center gap-1.5 bg-zinc-900">
            <ShieldCheck className="w-3 h-3 text-zinc-300" />
            <span className="text-[10px] font-mono text-zinc-300 uppercase tracking-widest">SVAMITVA Aligned</span>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex-1 flex justify-center">
          <VoiceSearchBar />
        </div>

        {/* Metrics Ticker - Terminal Style */}
        <div className="flex items-center gap-4 font-mono text-xs font-bold tracking-wider">
          <MetricItem label="SCANNED" value="400" />
          <MetricItem label="GHOSTS" value="31" />
          <MetricItem label="PHANTOMS" value="09" />
          <MetricItem label="DRIFTS" value="14" />
          
          <div className="px-3 py-1 border border-white bg-white text-black ml-2 uppercase">
            SYNC READY
          </div>
        </div>

      </div>
    </header>
  );
};

const MetricItem = ({ label, value }) => (
  <div className="flex items-center gap-1.5 text-zinc-300">
    <span className="text-zinc-600">[</span>
    <span>{label}:</span>
    <span className="text-white">{value}</span>
    <span className="text-zinc-600">]</span>
  </div>
);

export default Header;
