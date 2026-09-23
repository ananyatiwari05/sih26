import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { initialLedgerData } from '../data/mockData';
import { Terminal, ShieldAlert } from 'lucide-react';

const LedgerViewer = ({ isOpen, onClose }) => {
  const [ledger, setLedger] = useState(initialLedgerData);
  const [tamperedIdx, setTamperedIdx] = useState(null);

  const simulateTampering = (idx) => {
    const newLedger = [...ledger];
    newLedger[idx].tampered = true;
    newLedger[idx].hash = "ERR_HASH_MISMATCH";
    
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
          transition={{ type: 'tween', duration: 0.2 }}
          className="absolute bottom-16 left-1/2 -translate-x-1/2 w-[800px] max-w-[90vw] z-40 bg-black border border-white shadow-[8px_8px_0px_white] flex flex-col max-h-[50vh] pointer-events-auto rounded-none font-mono"
        >
          {/* Header */}
          <div className="p-3 border-b border-white flex items-center justify-between bg-zinc-900">
            <div className="flex items-center gap-3 text-white">
              <Terminal className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-widest">/VAR/LOG/IMMUTABLE_TRUST.LOG</span>
            </div>
            <div className="flex items-center gap-4">
              {tamperedIdx !== null && (
                <button onClick={resetLedger} className="text-[10px] px-2 py-0.5 border border-white hover:bg-white hover:text-black uppercase tracking-widest transition-colors">
                  &gt;_ RESET_STATE
                </button>
              )}
              <button onClick={onClose} className="text-zinc-400 hover:text-white text-[10px] uppercase font-bold tracking-widest">
                [X] CLOSE
              </button>
            </div>
          </div>

          {/* Terminal Logs */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2 text-xs">
            {ledger.map((block, idx) => (
              <div key={block.block} className={`flex flex-col border-l-2 pl-3 ${block.tampered ? 'border-zinc-500 text-zinc-400' : 'border-white text-white'}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-1 font-bold ${block.tampered ? 'bg-zinc-800 text-zinc-500' : 'bg-white text-black'}`}>
                    BLK_{block.block}
                  </span>
                  <span className="text-zinc-500">{block.timestamp}</span>
                  {block.tampered && idx === tamperedIdx && (
                    <span className="flex items-center gap-1 bg-white text-black px-1 animate-pulse font-bold ml-auto">
                      <ShieldAlert className="w-3 h-3" /> FATAL: CHAIN BROKEN
                    </span>
                  )}
                </div>
                
                <div className="grid grid-cols-12 gap-2 opacity-90">
                  <div className="col-span-2 text-zinc-500">HASH:</div>
                  <div className={`col-span-10 font-bold ${block.tampered ? 'line-through decoration-zinc-500' : ''}`}>
                    {block.hash}
                  </div>
                  
                  <div className="col-span-2 text-zinc-500">PREV:</div>
                  <div className="col-span-10 text-zinc-400">{block.prevHash}</div>
                  
                  <div className="col-span-2 text-zinc-500">ACTN:</div>
                  <div className="col-span-10">[{block.action}] ON {block.parcelId} BY {block.officerId}</div>
                </div>
                
                {!block.tampered && idx !== 0 && tamperedIdx === null && (
                  <button 
                    onClick={() => simulateTampering(idx)}
                    className="mt-2 self-start px-2 py-1 border border-zinc-700 text-zinc-500 hover:text-black hover:bg-white hover:border-white uppercase tracking-widest text-[9px] transition-colors"
                  >
                    &gt; sudo inject_fault --idx={idx}
                  </button>
                )}
                
                {idx !== ledger.length - 1 && (
                  <div className="text-zinc-700 my-1">|</div>
                )}
              </div>
            ))}
            <div className="text-zinc-500 animate-pulse mt-2">&gt;_ WAITING FOR NEW BLOCKS...</div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default LedgerViewer;
