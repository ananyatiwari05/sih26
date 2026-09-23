import React, { useState } from 'react';
import { Mic, Search, Square } from 'lucide-react';

const VoiceSearchBar = () => {
  const [isListening, setIsListening] = useState(false);

  const toggleListen = () => {
    setIsListening(!isListening);
  };

  return (
    <div className="relative flex items-center w-full max-w-md mx-4 font-mono">
      <div className="flex items-center w-full bg-black border border-zinc-700 px-3 py-1.5 focus-within:border-white transition-colors">
        <Search className="w-3.5 h-3.5 text-zinc-500 mr-2 rounded-none" />
        <input 
          type="text" 
          placeholder=">_ QUERY: 'Show ghost structures...'" 
          className="bg-transparent border-none outline-none text-white text-xs w-full placeholder:text-zinc-600 uppercase"
        />
        <button 
          onClick={toggleListen}
          className={`ml-2 p-1 border transition-colors ${isListening ? 'bg-white text-black border-white' : 'hover:bg-zinc-800 text-zinc-400 border-transparent'}`}
        >
          {isListening ? <Square className="w-3.5 h-3.5 fill-black" /> : <Mic className="w-3.5 h-3.5" />}
        </button>
      </div>
      {isListening && (
        <div className="absolute top-10 left-0 w-full bg-black border border-white p-2 text-[10px] text-white shadow-[4px_4px_0px_white] z-50">
          <div className="flex items-center gap-2 uppercase tracking-widest">
            <span className="w-2 h-2 bg-white animate-pulse"></span>
            REC // BHASHINI AI ACTIVE...
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceSearchBar;
