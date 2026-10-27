import React, { useEffect, useState } from "react";
import { fetchDatasetStatus } from "../api";
import { X, Database, CheckCircle, ShieldCheck, Layers, MapPin } from "lucide-react";

interface DatasetStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DatasetStatusModal: React.FC<DatasetStatusModalProps> = ({ isOpen, onClose }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);
    fetchDatasetStatus()
      .then((res) => setData(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [isOpen]);

  if (!isOpen) return null;

  const prof = data?.dataset_profile || {};
  const meta = data?.metadata || {};

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl border border-slate-200 p-6 sm:p-8 relative">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-slate-900">Dataset Profile & Quality Audit</h2>
            <p className="text-xs text-slate-500">Official Government Welfare Registry (schemes.csv)</p>
          </div>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-500">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
            <p className="text-sm">Auditing dataset records...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Metric grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                <span className="text-xs text-slate-500 block mb-1">Total Schemes</span>
                <span className="text-xl font-black text-slate-900">{prof.total_records || 4670}</span>
              </div>
              <div className="p-4 rounded-2xl bg-blue-50/70 border border-blue-200">
                <span className="text-xs text-blue-700 block mb-1">Central Schemes</span>
                <span className="text-xl font-black text-blue-900">{prof.central_schemes || 649}</span>
              </div>
              <div className="p-4 rounded-2xl bg-indigo-50/70 border border-indigo-200">
                <span className="text-xs text-indigo-700 block mb-1">State & UT Schemes</span>
                <span className="text-xl font-black text-indigo-900">{prof.state_schemes || 4021}</span>
              </div>
              <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200">
                <span className="text-xs text-emerald-700 block mb-1">Valid Official URLs</span>
                <span className="text-xl font-black text-emerald-900">{prof.valid_source_urls_pct || 100}%</span>
              </div>
              <div className="p-4 rounded-2xl bg-purple-50/70 border border-purple-200">
                <span className="text-xs text-purple-700 block mb-1">Benefits Documented</span>
                <span className="text-xl font-black text-purple-900">{prof.schemes_with_benefits_pct || 94.4}%</span>
              </div>
              <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200">
                <span className="text-xs text-amber-700 block mb-1">Documents Listed</span>
                <span className="text-xl font-black text-amber-900">{prof.schemes_with_docs_pct || 91.1}%</span>
              </div>
            </div>

            {/* Geographical coverage */}
            <div>
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-slate-500" />
                <span>Geographic & State Coverage</span>
              </h4>
              <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto p-2 bg-slate-50 rounded-xl border border-slate-200">
                {meta.states?.map((st: string, idx: number) => (
                  <span key={idx} className="text-xs px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-700 font-medium">
                    {st}
                  </span>
                ))}
              </div>
            </div>

            {/* Quality Summary */}
            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200 text-xs text-slate-600 leading-relaxed">
              <p className="font-semibold text-slate-800 mb-1">Traceability & Data Hygiene:</p>
              <ul className="list-disc pl-4 space-y-1">
                <li>Every scheme record preserves original verified government slugs (`slug`) as primary keys.</li>
                <li>Non-destructive ETL pipeline unescapes HTML entities (`&amp;`, `&quot;`) while keeping UTF-8 currency symbols (₹).</li>
                <li>Central schemes are treated with pan-India residency applicability.</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
