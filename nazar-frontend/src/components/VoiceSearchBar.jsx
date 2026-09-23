import React, { useState } from 'react';
import { Mic, Search, AudioLines } from 'lucide-react';
import { motion } from 'framer-motion';

const VoiceSearchBar = () => {
  const [isListening, setIsListening] = useState(false);

  const toggleListen = () => {
    setIsListening(!isListening);
  };

  return (
    <div className="relative flex items-center w-full max-w-md mx-4">
      <div className="flex items-center w-full bg-slate-800/80 border border-slate-600/50 rounded-full px-4 py-2 shadow-inner focus-within:border-emerald-500/50 transition-colors">
        <Search className="w-4 h-4 text-slate-400 mr-2" />
        <input 
          type="text" 
          placeholder="E.g., 'Ramgarh gaon mein ghost structures dikhao'" 
          className="bg-transparent border-none outline-none text-slate-200 text-sm w-full placeholder:text-slate-500"
        />
        <button 
          onClick={toggleListen}
          className={`ml-2 p-1.5 rounded-full transition-colors ${isListening ? 'bg-emerald-500/20 text-emerald-400' : 'hover:bg-slate-700 text-slate-400'}`}
        >
          {isListening ? <AudioLines className="w-4 h-4 animate-pulse" /> : <Mic className="w-4 h-4" />}
        </button>
      </div>
      {isListening && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute top-12 left-0 w-full bg-slate-800/95 border border-emerald-500/30 rounded-lg p-3 text-xs text-emerald-400 shadow-xl backdrop-blur-md"
        >
          <div className="flex items-center gap-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            Listening (Bhashini AI active)...
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default VoiceSearchBar;
