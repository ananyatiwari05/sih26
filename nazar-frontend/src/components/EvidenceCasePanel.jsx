import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { X, AlertOctagon, CheckCircle2, ShieldAlert, Navigation, FilePenLine } from 'lucide-react';
import { elevationChartData } from '../data/mockData';

const EvidenceCasePanel = ({ selectedFeature, onClose }) => {
  if (!selectedFeature) return null;

  const { properties } = selectedFeature;
  const isGhost = properties.type === 'GHOST_STRUCTURE';
  const isPhantom = properties.type === 'PHANTOM_RECORD';
  const isDrift = properties.type === 'BOUNDARY_DRIFT';
  const isVerified = properties.type === 'VERIFIED';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: '100%', opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: '100%', opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="absolute top-0 right-0 h-full w-[450px] z-40 bg-slate-900/90 backdrop-blur-xl border-l border-slate-700/60 shadow-2xl flex flex-col pointer-events-auto overflow-y-auto"
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-700/60 flex items-center justify-between sticky top-0 bg-slate-900/95 z-10">
          <div>
            <h2 className="text-xl font-bold text-slate-100 font-mono tracking-wide">Case #{properties.id}</h2>
            <p className="text-xs text-slate-400 uppercase tracking-widest mt-1">SVAMITVA Reconciliation</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-full hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 flex-1 flex flex-col gap-6">
          
          {/* AI Verdict Badge */}
          <div className={`p-4 rounded-xl border flex items-start gap-4 ${
            isGhost ? 'bg-red-950/40 border-red-500/50' : 
            isPhantom ? 'bg-amber-950/40 border-amber-500/50' : 
            isDrift ? 'bg-yellow-950/40 border-yellow-500/50' : 
            'bg-emerald-950/40 border-emerald-500/50'
          }`}>
            <div className={`mt-1 ${
              isGhost ? 'text-red-400' : isPhantom ? 'text-amber-400' : isDrift ? 'text-yellow-400' : 'text-emerald-400'
            }`}>
              {isVerified ? <CheckCircle2 className="w-6 h-6" /> : <ShieldAlert className="w-6 h-6" />}
            </div>
            <div>
              <h3 className={`text-sm font-bold uppercase tracking-wider ${
                isGhost ? 'text-red-400' : isPhantom ? 'text-amber-400' : isDrift ? 'text-yellow-400' : 'text-emerald-400'
              }`}>
                {isGhost ? 'Ghost Structure Detected' : 
                 isPhantom ? 'Phantom Record Detected' : 
                 isDrift ? 'Boundary Drift Detected' : 
                 'Verified Clean Parcel'}
                <span className="ml-2 text-slate-300 text-xs">({properties.confidence}% Conf)</span>
              </h3>
              <p className="text-sm text-slate-300 mt-2 leading-relaxed">
                {properties.description}
              </p>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-4">
            <DetailBox label="Survey Year" value={properties.surveyYear} />
            <DetailBox label="Calculated Area" value={`${properties.area || '--'} sq.m`} />
            <DetailBox label="Current Status" value={properties.status} />
            {properties.height && <DetailBox label="Peak Elevation" value={`${properties.height}m`} />}
            {properties.driftMargin && <DetailBox label="Drift Margin" value={`${properties.driftMargin}m`} />}
          </div>

          {/* Dual View Exhibit (Mockup) */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Visual Evidence Exhibit</h4>
            <div className="h-48 rounded-xl overflow-hidden border border-slate-700/60 relative group bg-slate-800 flex items-center justify-center">
              {/* This would be an actual image in reality, just simulating with CSS here */}
              <div className="absolute inset-0 opacity-40 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] mix-blend-overlay"></div>
              <div className="absolute inset-4 border-2 border-dashed border-slate-500 rounded-lg flex items-center justify-center">
                <span className="text-slate-500 font-mono text-sm">Orthophoto vs Cadastral Overlay</span>
              </div>
              {isGhost && (
                <div className="absolute w-20 h-20 bg-red-500/30 border-2 border-red-500/80 rounded-md rotate-12 flex items-center justify-center">
                  <AlertOctagon className="text-red-400 w-8 h-8 opacity-70" />
                </div>
              )}
            </div>
          </div>

          {/* Elevation Chart for Ghosts */}
          {(isGhost || isDrift) && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                <span>nDSM Height Profile</span>
                {properties.height && <span className="text-red-400">Peak: {properties.height}m</span>}
              </h4>
              <div className="h-40 bg-slate-800/50 rounded-xl p-3 border border-slate-700/60">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={elevationChartData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorStructure" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorGround" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.5}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="distance" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                      itemStyle={{ color: '#f1f5f9' }}
                    />
                    <ReferenceLine y={0} stroke="#334155" />
                    <Area type="monotone" dataKey="ground" stroke="#10b981" fillOpacity={1} fill="url(#colorGround)" />
                    <Area type="monotone" dataKey="structure" stroke="#ef4444" fillOpacity={1} fill="url(#colorStructure)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

        </div>

        {/* Action Controls */}
        <div className="p-5 border-t border-slate-700/60 bg-slate-900/95 sticky bottom-0 flex flex-col gap-3">
          {isVerified ? (
             <button className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors">
               <CheckCircle2 className="w-5 h-5" />
               Ready for SVAMITVA Sync
             </button>
          ) : (
            <>
              <div className="flex gap-3">
                <button className="flex-1 py-2.5 px-3 bg-red-900/40 hover:bg-red-800/60 border border-red-500/50 text-red-100 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors text-sm">
                  <AlertOctagon className="w-4 h-4" /> Reject Anomaly
                </button>
                <button className="flex-1 py-2.5 px-3 bg-emerald-900/40 hover:bg-emerald-800/60 border border-emerald-500/50 text-emerald-100 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors text-sm">
                  <CheckCircle2 className="w-4 h-4" /> Accept Reality
                </button>
              </div>
              <button className="w-full py-2.5 px-4 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors text-sm">
                <FilePenLine className="w-4 h-4" /> Edit Polygon Boundary
              </button>
            </>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

const DetailBox = ({ label, value }) => (
  <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-3">
    <div className="text-[10px] text-slate-400 uppercase tracking-widest mb-1">{label}</div>
    <div className="text-sm font-semibold font-mono text-slate-200">{value}</div>
  </div>
);

export default EvidenceCasePanel;
