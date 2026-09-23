import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { X, AlertOctagon, CheckSquare, ShieldAlert, Navigation, Edit2 } from 'lucide-react';
import { elevationChartData } from '../data/mockData';

const EvidenceCasePanel = ({ selectedFeature, onClose }) => {
  if (!selectedFeature) return null;

  const { properties } = selectedFeature;
  const isGhost = properties.type === 'GHOST_STRUCTURE';
  const isPhantom = properties.type === 'PHANTOM_RECORD';
  const isDrift = properties.type === 'BOUNDARY_DRIFT';
  const isVerified = properties.type === 'VERIFIED';

  const verdictText = isGhost ? 'GHOST STRUCTURE DETECTED' : 
                      isPhantom ? 'PHANTOM RECORD DETECTED' : 
                      isDrift ? 'BOUNDARY DRIFT DETECTED' : 
                      'VERIFIED CLEAN PARCEL';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: '100%', opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: '100%', opacity: 0 }}
        transition={{ type: 'tween', duration: 0.2 }}
        className="absolute top-0 right-0 h-full w-[450px] z-40 bg-black border-l border-zinc-700 shadow-[-8px_0px_0px_rgba(255,255,255,0.05)] flex flex-col pointer-events-auto font-sans text-white rounded-none"
      >
        {/* Header */}
        <div className="p-4 border-b border-zinc-700 flex items-center justify-between sticky top-0 bg-black z-10">
          <div>
            <h2 className="text-xl font-bold font-mono tracking-tighter uppercase">CASE::{properties.id}</h2>
            <p className="text-[10px] text-zinc-500 font-mono uppercase tracking-widest mt-1">SVAMITVA Recon // {properties.surveyYear}</p>
          </div>
          <button 
            onClick={onClose}
            className="p-1 border border-zinc-700 hover:bg-white hover:text-black transition-colors rounded-none"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 flex-1 flex flex-col gap-6 overflow-y-auto">
          
          {/* AI Verdict Badge - Brutalist High Contrast */}
          <div className="border border-white p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-white text-black p-1">
                {isVerified ? <CheckSquare className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5" />}
              </div>
              <div className="bg-white text-black font-bold p-1 px-2 uppercase font-mono text-sm tracking-tight w-full">
                VERDICT: {verdictText}
              </div>
            </div>
            <div className="font-mono text-xs text-zinc-400 uppercase tracking-widest mb-2">
              CONFIDENCE: {properties.confidence}%
            </div>
            <p className="text-sm text-zinc-300 leading-relaxed font-mono">
              &gt; {properties.description}
            </p>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-3">
            <DetailBox label="Survey Year" value={properties.surveyYear} />
            <DetailBox label="Calculated Area" value={`${properties.area || '--'} SQ.M`} />
            <DetailBox label="Current Status" value={properties.status} />
            {properties.height && <DetailBox label="Peak Elevation" value={`${properties.height}M`} />}
            {properties.driftMargin && <DetailBox label="Drift Margin" value={`${properties.driftMargin}M`} />}
          </div>

          {/* Dual View Exhibit (Mockup) */}
          <div className="space-y-2">
            <h4 className="text-[10px] font-bold text-zinc-500 font-mono uppercase tracking-widest">Visual Evidence Exhibit</h4>
            <div className="h-48 border border-zinc-700 relative bg-zinc-900 flex items-center justify-center overflow-hidden">
              <div className="absolute inset-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] mix-blend-overlay grayscale"></div>
              <div className="absolute inset-4 border border-dashed border-zinc-500 flex items-center justify-center">
                <span className="text-zinc-600 font-mono text-xs uppercase tracking-widest">Orthophoto Overlay</span>
              </div>
              {isGhost && (
                <div className="absolute w-20 h-20 bg-transparent border-2 border-dashed border-white rotate-12 flex items-center justify-center shadow-[4px_4px_0px_white]">
                  <AlertOctagon className="text-white w-8 h-8 opacity-70" />
                </div>
              )}
            </div>
          </div>

          {/* Elevation Chart for Ghosts */}
          {(isGhost || isDrift) && (
            <div className="space-y-2">
              <h4 className="text-[10px] font-bold text-zinc-500 font-mono uppercase tracking-widest flex items-center justify-between">
                <span>nDSM Height Profile</span>
                {properties.height && <span className="text-white">PEAK: {properties.height}M</span>}
              </h4>
              <div className="h-40 bg-black border border-zinc-700 p-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={elevationChartData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorStructure" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ffffff" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#ffffff" stopOpacity={0}/>
                      </linearGradient>
                      <pattern id="diagonalHatch" patternUnits="userSpaceOnUse" width="4" height="4">
                        <path d="M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2" stroke="#52525B" strokeWidth="1" />
                      </pattern>
                    </defs>
                    <XAxis dataKey="distance" stroke="#52525B" fontSize={10} tickLine={false} axisLine={false} fontFamily="monospace" />
                    <YAxis stroke="#52525B" fontSize={10} tickLine={false} axisLine={false} fontFamily="monospace" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#000000', borderColor: '#ffffff', borderRadius: '0', fontFamily: 'monospace' }}
                      itemStyle={{ color: '#ffffff' }}
                    />
                    <ReferenceLine y={0} stroke="#ffffff" strokeDasharray="3 3" />
                    <Area type="step" dataKey="ground" stroke="#52525B" fillOpacity={1} fill="url(#diagonalHatch)" />
                    <Area type="step" dataKey="structure" stroke="#ffffff" fillOpacity={1} fill="url(#colorStructure)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

        </div>

        {/* Action Controls */}
        <div className="p-4 border-t border-zinc-700 bg-black sticky bottom-0 flex flex-col gap-3">
          {isVerified ? (
             <button className="w-full py-3 px-4 bg-white text-black font-bold uppercase tracking-widest text-sm flex items-center justify-center gap-2 transition-colors border border-transparent hover:bg-black hover:text-white hover:border-white">
               <CheckSquare className="w-4 h-4" />
               SYNC TO SVAMITVA
             </button>
          ) : (
            <>
              <div className="flex gap-3">
                <button className="flex-1 py-2.5 px-3 bg-black text-white border border-zinc-600 hover:border-white font-mono uppercase tracking-widest flex items-center justify-center gap-2 transition-colors text-[10px]">
                  <X className="w-3.5 h-3.5" /> REJECT
                </button>
                <button className="flex-1 py-2.5 px-3 bg-white text-black border border-white hover:bg-black hover:text-white font-mono uppercase tracking-widest flex items-center justify-center gap-2 transition-colors text-[10px]">
                  <CheckSquare className="w-3.5 h-3.5" /> ACCEPT
                </button>
              </div>
              <button className="w-full py-2.5 px-4 bg-zinc-900 text-zinc-300 border border-zinc-800 hover:border-zinc-500 font-mono uppercase tracking-widest flex items-center justify-center gap-2 transition-colors text-[10px]">
                <Edit2 className="w-3 h-3" /> EDIT POLYGON
              </button>
            </>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

const DetailBox = ({ label, value }) => (
  <div className="border border-zinc-800 p-2">
    <div className="text-[9px] text-zinc-500 font-mono uppercase tracking-widest mb-1">{label}</div>
    <div className="text-xs font-bold font-mono text-white truncate uppercase">{value}</div>
  </div>
);

export default EvidenceCasePanel;
