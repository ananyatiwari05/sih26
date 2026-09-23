import React from 'react';
import { ShieldCheck, Crosshair, AlertTriangle, Layers, FileWarning } from 'lucide-react';
import VoiceSearchBar from './VoiceSearchBar';

const Header = () => {
  return (
    <header className="absolute top-0 left-0 w-full z-50 p-4 pointer-events-none">
      <div className="flex items-center justify-between pointer-events-auto">
        
        {/* Branding & Badge */}
        <div className="flex items-center gap-4">
          <div className="bg-slate-900/85 backdrop-blur-md border border-slate-700/60 rounded-xl p-3 shadow-2xl flex items-center gap-3">
            <div className="bg-emerald-500/20 p-2 rounded-lg border border-emerald-500/30">
              <Crosshair className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-wider text-slate-100 uppercase font-mono">Nazar</h1>
              <p className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Ground Truth Engine</p>
            </div>
          </div>
          
          <div className="bg-blue-900/40 backdrop-blur-md border border-blue-500/30 rounded-full px-3 py-1 flex items-center gap-2 shadow-lg">
            <ShieldCheck className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-semibold text-blue-200 uppercase tracking-wider">SVAMITVA Scheme Aligned</span>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex-1 flex justify-center">
          <VoiceSearchBar />
        </div>

        {/* Metrics Ticker */}
        <div className="bg-slate-900/85 backdrop-blur-md border border-slate-700/60 rounded-xl shadow-2xl flex items-center overflow-hidden h-14">
          <MetricItem icon={<Layers className="w-4 h-4 text-slate-400"/>} label="Parcels Scanned" value="400" />
          <MetricItem icon={<AlertTriangle className="w-4 h-4 text-red-400"/>} label="Ghosts" value="31" highlight="text-red-400" />
          <MetricItem icon={<FileWarning className="w-4 h-4 text-amber-500"/>} label="Phantoms" value="9" highlight="text-amber-500" />
          <MetricItem icon={<Crosshair className="w-4 h-4 text-yellow-400"/>} label="Drifts" value="14" highlight="text-yellow-400" />
          
          <div className="px-4 py-2 bg-emerald-950/40 border-l border-slate-700/60 h-full flex items-center justify-center">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse"></div>
              <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Sync Ready</span>
            </div>
          </div>
        </div>

      </div>
    </header>
  );
};

const MetricItem = ({ icon, label, value, highlight = "text-slate-200" }) => (
  <div className="px-4 py-2 border-r border-slate-700/60 last:border-0 h-full flex flex-col justify-center">
    <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
      {icon} {label}
    </div>
    <div className={`text-lg font-bold font-mono leading-tight ${highlight}`}>
      {value}
    </div>
  </div>
);

export default Header;
