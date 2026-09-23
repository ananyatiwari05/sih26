import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, X, FileJson, MapPin, Printer } from 'lucide-react';

const ExportModal = ({ isOpen, onClose, selectedFeature }) => {
  if (!isOpen) return null;

  const handleDownload = (format) => {
    alert(`Exporting Sampatti Patrak as ${format.toUpperCase()}...`);
    onClose();
  };

  const isVerified = selectedFeature?.properties?.type === 'VERIFIED';
  const parcelId = selectedFeature?.properties?.id || 'UNKNOWN';

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center pointer-events-auto">
        <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose}></div>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ type: 'tween', duration: 0.15 }}
          className="relative bg-black w-[550px] max-w-[90vw] border border-white shadow-[8px_8px_0px_white] flex flex-col font-mono rounded-none text-white"
        >
          {/* Header */}
          <div className="bg-white text-black p-4 flex justify-between items-center relative overflow-hidden border-b border-black">
            <div className="absolute top-0 right-0 opacity-10">
              <MapPin className="w-32 h-32 -mt-10 -mr-10" />
            </div>
            <div className="relative z-10">
              <h2 className="text-2xl font-bold uppercase tracking-tighter">SAMPATTI_PATRAK.PDF</h2>
              <p className="text-[10px] uppercase tracking-widest font-bold">SVAMITVA Scheme - Property Card</p>
            </div>
            <button onClick={onClose} className="p-1 border border-black hover:bg-black hover:text-white transition-colors relative z-10 rounded-none">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-8 space-y-6">
            <div className="text-center space-y-1 border-b-2 border-dashed border-zinc-700 pb-4">
              <div className="text-[10px] uppercase tracking-widest text-zinc-500">Official Record of Rights</div>
              <div className="text-xl font-bold tracking-tight">PARCEL_ID: {parcelId}</div>
            </div>

            <div className="grid grid-cols-2 gap-y-6 gap-x-8 text-sm">
              <div className="space-y-1">
                <div className="text-[9px] uppercase text-zinc-500 tracking-widest">OWNER_NAME</div>
                <div className="font-bold border-b border-zinc-700 pb-1">{selectedFeature?.properties?.owner || 'GOVT OF INDIA'}</div>
              </div>
              <div className="space-y-1">
                <div className="text-[9px] uppercase text-zinc-500 tracking-widest">TOTAL_AREA</div>
                <div className="font-bold border-b border-zinc-700 pb-1">{selectedFeature?.properties?.area || '--'} SQ.M</div>
              </div>
              <div className="space-y-1">
                <div className="text-[9px] uppercase text-zinc-500 tracking-widest">SURVEY_YEAR</div>
                <div className="font-bold border-b border-zinc-700 pb-1">{selectedFeature?.properties?.surveyYear || '2026'}</div>
              </div>
              <div className="space-y-1">
                <div className="text-[9px] uppercase text-zinc-500 tracking-widest">LEGAL_STATUS</div>
                <div className={`font-bold border-b border-zinc-700 pb-1 ${isVerified ? 'text-white' : 'text-zinc-500 line-through'}`}>
                  {isVerified ? 'VERIFIED' : 'DISPUTED'}
                </div>
              </div>
            </div>

            <div className="bg-zinc-900 p-4 border border-zinc-700 text-[10px] text-zinc-400 uppercase tracking-widest leading-relaxed">
              "THIS DOCUMENT IS A DIGITALLY GENERATED PROVISIONAL PROPERTY CARD BASED ON DRONE SURVEYS UNDER THE SVAMITVA SCHEME. FINAL LEGAL VALIDITY IS SUBJECT TO GROUND TRUTHING BY LOCAL AUTHORITIES."
            </div>
          </div>

          {/* Action Footer */}
          <div className="p-4 flex gap-3 border-t border-zinc-700 bg-zinc-950">
            <button 
              onClick={() => handleDownload('pdf')}
              className="flex-1 bg-white hover:bg-zinc-300 text-black py-3 px-4 flex items-center justify-center gap-2 font-bold text-xs uppercase tracking-widest transition-colors rounded-none border border-transparent"
            >
              <Download className="w-4 h-4" /> EXPORT PDF
            </button>
            <button 
              onClick={() => handleDownload('geojson')}
              className="bg-black hover:bg-zinc-900 text-white border border-white py-3 px-4 flex items-center justify-center gap-2 font-bold text-xs uppercase tracking-widest transition-colors rounded-none"
            >
              <FileJson className="w-4 h-4" /> GEOJSON
            </button>
            <button 
              onClick={() => window.print()}
              className="bg-zinc-900 hover:bg-zinc-800 text-zinc-400 border border-zinc-700 py-3 px-4 flex items-center justify-center transition-colors rounded-none"
              title="Print"
            >
              <Printer className="w-4 h-4" />
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default ExportModal;
