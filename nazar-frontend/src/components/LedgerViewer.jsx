import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { initialLedgerData } from '../data/mockData';
import { Database, Link, AlertTriangle, Fingerprint, Activity } from 'lucide-react';

const LedgerViewer = ({ isOpen, onClose }) => {
  const [ledger, setLedger] = useState(initialLedgerData);
  const [tamperedIdx, setTamperedIdx] = useState(null);

  const simulateTampering = (idx) => {
    const newLedger = [...ledger];
    // Tamper the specific block
    newLedger[idx].tampered = true;
    newLedger[idx].hash = "INVALID_HASH_CORRUPTED";
    
    // Corrupt all subsequent (newer) blocks because the chain is broken
    for (let i = idx - 1; i >= 0; i--) {
      newLedger[i].tampered = true;
    }
    
    setLedger(newLedger);
    setTamperedIdx(idx);
  };

  const resetLedger = () => {
    setLedger(initialLedgerData);
    setTamperedIdx(null);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ y: '100%', opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: '100%', opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="absolute bottom-20 left-1/2 -translate-x-1/2 w-[800px] max-w-[90vw] z-40 bg-slate-900/95 backdrop-blur-xl border border-slate-700/60 shadow-2xl rounded-xl overflow-hidden flex flex-col max-h-[50vh] pointer-events-auto"
        >
          {/* Header */}
          <div className="p-4 border-b border-slate-700/60 flex items-center justify-between bg-slate-800/50">
            <div className="flex items-center gap-3">
              <Database className="w-5 h-5 text-blue-400" />
              <div>
                <h2 className="text-sm font-bold text-slate-100 font-mono tracking-wide">Immutable Trust Ledger</h2>
                <p className="text-[10px] text-slate-400 uppercase tracking-widest">SHA-256 Hash Chain</p>
              </div>
            </div>
            {tamperedIdx !== null && (
              <button onClick={resetLedger} className="text-xs px-3 py-1 bg-blue-900/40 text-blue-300 border border-blue-500/30 rounded hover:bg-blue-800/60 transition-colors">
                Reset Ledger
              </button>
            )}
            <button onClick={onClose} className="text-slate-400 hover:text-slate-200 text-xs uppercase font-bold tracking-widest">
              Close
            </button>
          </div>

          {/* Blocks */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {ledger.map((block, idx) => (
              <div key={block.block} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center border ${
                    block.tampered ? 'bg-red-950/50 border-red-500/50 text-red-400' : 'bg-blue-950/50 border-blue-500/50 text-blue-400'
                  }`}>
                    <Link className="w-4 h-4" />
                  </div>
                  {idx !== ledger.length - 1 && (
                    <div className={`w-0.5 h-full my-1 ${block.tampered ? 'bg-red-500/50' : 'bg-blue-500/30'}`}></div>
                  )}
                </div>
                
                <div className={`flex-1 p-4 rounded-lg border flex justify-between items-center ${
                  block.tampered ? 'bg-red-900/10 border-red-500/40' : 'bg-slate-800/40 border-slate-700/50'
                }`}>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                        block.tampered ? 'bg-red-500/20 text-red-400' : 'bg-slate-700 text-slate-300'
                      }`}>
                        Block #{block.block}
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">{block.timestamp}</span>
                    </div>
                    <div className="text-sm font-mono text-slate-300 flex items-center gap-2">
                      <Fingerprint className="w-4 h-4 text-slate-500" />
                      Hash: <span className={block.tampered ? 'text-red-400' : 'text-emerald-400'}>{block.hash}</span>
                    </div>
                    <div className="text-xs font-mono text-slate-500">
                      Prev: {block.prevHash}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-slate-400 mt-2">
                      <span><span className="text-slate-500">Officer:</span> {block.officerId}</span>
                      <span><span className="text-slate-500">Action:</span> {block.action}</span>
                      <span><span className="text-slate-500">Target:</span> {block.parcelId}</span>
                    </div>
                  </div>
                  
                  {!block.tampered && idx !== 0 && tamperedIdx === null && (
                    <button 
                      onClick={() => simulateTampering(idx)}
                      className="px-3 py-2 bg-red-950/40 hover:bg-red-900/60 border border-red-500/30 text-red-400 text-xs rounded transition-colors flex items-center gap-2"
                    >
                      <AlertTriangle className="w-3 h-3" /> Simulate Tampering
                    </button>
                  )}
                  {block.tampered && idx === tamperedIdx && (
                    <div className="text-red-500 text-xs font-bold animate-pulse flex items-center gap-1">
                      <Activity className="w-4 h-4" /> CHAIN BROKEN
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default LedgerViewer;
