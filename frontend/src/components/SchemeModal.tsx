import React, { useEffect, useState } from "react";
import { SchemeDetail } from "../types";
import { fetchSchemeDetail } from "../api";
import { X, ExternalLink, CheckCircle, FileText, ListOrdered, Landmark, AlertTriangle } from "lucide-react";

interface SchemeModalProps {
  schemeId: string | null;
  onClose: () => void;
}

export const SchemeModal: React.FC<SchemeModalProps> = ({ schemeId, onClose }) => {
  const [detail, setDetail] = useState<SchemeDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!schemeId) {
      setDetail(null);
      return;
    }
    setLoading(true);
    setError(null);
    fetchSchemeDetail(schemeId)
      .then((data) => setDetail(data))
      .catch((err) => setError(err.message || "Failed to load scheme details"))
      .finally(() => setLoading(false));
  }, [schemeId]);

  if (!schemeId) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200 p-6 sm:p-8 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center text-slate-500">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
            <p className="text-sm">Fetching verified scheme records...</p>
          </div>
        ) : error ? (
          <div className="py-12 text-center text-rose-600">
            <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
            <p className="font-semibold">{error}</p>
          </div>
        ) : detail ? (
          <div>
            {/* Header info */}
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
                {detail.level} Scheme
              </span>
              {detail.state && (
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                  {detail.state}
                </span>
              )}
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-800">
                Benefit: {detail.benefit_type}
              </span>
            </div>

            <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 mb-2">
              {detail.name}
            </h2>

            {detail.department && (
              <p className="text-xs sm:text-sm text-slate-500 mb-4 flex items-center gap-1.5">
                <Landmark className="w-4 h-4 text-slate-400" />
                <span>Implementing Department: <strong>{detail.department}</strong></span>
              </p>
            )}

            {/* Brief Description */}
            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200 mb-6">
              <p className="text-sm text-slate-700 leading-relaxed">
                {detail.brief_description || detail.detailed_description}
              </p>
            </div>

            {/* Benefits */}
            {detail.benefits && detail.benefits.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                  <span>Scheme Benefits</span>
                </h4>
                <ul className="space-y-1.5 pl-2">
                  {detail.benefits.map((b, i) => (
                    <li key={i} className="text-xs sm:text-sm text-slate-700 flex items-start gap-2">
                      <span className="text-emerald-500 font-bold">•</span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Eligibility Requirements */}
            <div className="mb-6">
              <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-blue-600" />
                <span>Eligibility Criteria</span>
              </h4>
              <div className="bg-blue-50/50 rounded-xl p-3 border border-blue-100 text-xs sm:text-sm text-slate-800 whitespace-pre-line leading-relaxed">
                {detail.eligibility_text || "General eligibility applies as per departmental notifications."}
              </div>
            </div>

            {/* Required Documents */}
            {detail.documents_required && detail.documents_required.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-purple-600" />
                  <span>Documents Required</span>
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {detail.documents_required.map((doc, i) => (
                    <div key={i} className="bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-xs text-slate-700 flex items-start gap-2">
                      <span className="text-purple-600 font-semibold">{i + 1}.</span>
                      <span>{doc}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Application Process */}
            {detail.application_steps && detail.application_steps.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <ListOrdered className="w-4 h-4 text-indigo-600" />
                  <span>Application Procedure ({detail.application_mode} Mode)</span>
                </h4>
                <div className="space-y-2">
                  {detail.application_steps.map((step, i) => (
                    <div key={i} className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs sm:text-sm text-slate-700 flex items-start gap-3">
                      <span className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xs">
                        {i + 1}
                      </span>
                      <span className="leading-snug">{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Official Source Link & Disclaimer */}
            <div className="mt-8 pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
              <p className="text-xs text-slate-400">
                Official source data: <strong>myScheme.gov.in</strong>
              </p>
              {detail.source_url && (
                <a
                  href={detail.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-semibold text-sm shadow-sm transition-all"
                >
                  <span>Open Official Application Portal</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
