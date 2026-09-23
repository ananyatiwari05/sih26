import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, X, FileJson, MapPin, Printer } from 'lucide-react';

const ExportModal = ({ isOpen, onClose, selectedFeature }) => {
  if (!isOpen) return null;

  const handleDownload = (format) => {
    // In a real app, this would trigger an actual download
    alert(`Exporting Sampatti Patrak as ${format.toUpperCase()}...`);
    onClose();
  };

  const isVerified = selectedFeature?.properties?.type === 'VERIFIED';
  const parcelId = selectedFeature?.properties?.id || 'UNKNOWN';

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center pointer-events-auto">
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose}></div>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="relative bg-slate-100 w-[500px] max-w-[90vw] rounded-sm shadow-2xl overflow-hidden flex flex-col font-serif"
        >
          {/* Header */}
          <div className="bg-emerald-800 text-emerald-50 p-4 flex justify-between items-center relative overflow-hidden">
            <div className="absolute top-0 right-0 opacity-10">
              <MapPin className="w-32 h-32 -mt-10 -mr-10" />
            </div>
            <div className="relative z-10">
              <h2 className="text-xl font-bold uppercase tracking-wider">Sampatti Patrak</h2>
              <p className="text-xs uppercase tracking-widest opacity-80">SVAMITVA Scheme - Property Card</p>
            </div>
            <button onClick={onClose} className="p-1 hover:bg-emerald-700 rounded transition-colors relative z-10">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-8 text-slate-800 space-y-6">
            <div className="text-center space-y-1 border-b-2 border-emerald-800/20 pb-4">
              <div className="text-xs uppercase tracking-widest text-slate-500 font-sans">Official Record of Rights</div>
              <div className="text-2xl font-bold tracking-tight">Parcel ID: {parcelId}</div>
            </div>

            <div className="grid grid-cols-2 gap-y-4 gap-x-8 text-sm">
              <div className="space-y-1">
                <div className="text-[10px] uppercase text-slate-500 font-sans">Owner Name</div>
                <div className="font-bold border-b border-slate-300 pb-1">{selectedFeature?.properties?.owner || 'Govt of India'}</div>
              </div>
              <div className="space-y-1">
                <div className="text-[10px] uppercase text-slate-500 font-sans">Total Area</div>
                <div className="font-bold border-b border-slate-300 pb-1">{selectedFeature?.properties?.area || '--'} sq.m</div>
              </div>
              <div className="space-y-1">
                <div className="text-[10px] uppercase text-slate-500 font-sans">Survey Year</div>
                <div className="font-bold border-b border-slate-300 pb-1">{selectedFeature?.properties?.surveyYear || '2026'}</div>
              </div>
              <div className="space-y-1">
                <div className="text-[10px] uppercase text-slate-500 font-sans">Status</div>
                <div className={`font-bold border-b border-slate-300 pb-1 ${isVerified ? 'text-emerald-700' : 'text-red-700'}`}>
                  {isVerified ? 'VERIFIED' : 'DISPUTED / PENDING'}
                </div>
              </div>
            </div>

            <div className="bg-slate-100 p-4 border border-slate-300 text-xs text-slate-600 italic">
              "This document is a digitally generated provisional property card based on drone surveys under the SVAMITVA scheme. Final legal validity is subject to ground truthing by local authorities."
            </div>
          </div>

          {/* Action Footer */}
          <div className="bg-slate-200 p-4 flex gap-3 font-sans">
            <button 
              onClick={() => handleDownload('pdf')}
              className="flex-1 bg-emerald-700 hover:bg-emerald-800 text-white py-2.5 px-4 flex items-center justify-center gap-2 font-semibold text-sm transition-colors rounded shadow"
            >
              <Download className="w-4 h-4" /> Download PDF
            </button>
            <button 
              onClick={() => handleDownload('geojson')}
              className="bg-slate-700 hover:bg-slate-800 text-white py-2.5 px-4 flex items-center justify-center gap-2 font-semibold text-sm transition-colors rounded shadow"
            >
              <FileJson className="w-4 h-4" /> Export GeoJSON
            </button>
            <button 
              onClick={() => window.print()}
              className="bg-slate-300 hover:bg-slate-400 text-slate-800 py-2.5 px-4 flex items-center justify-center transition-colors rounded shadow"
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
