import React from "react";
import { X, ShieldCheck, Cpu, BookOpen, AlertCircle, Sparkles } from "lucide-react";

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AboutModal: React.FC<AboutModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

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
          <div className="w-10 h-10 rounded-xl bg-blue-700 text-white flex items-center justify-center shadow-md">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-slate-900">About BenefitBridge AI</h2>
            <p className="text-xs text-slate-500">A Multi-Agent RAG Framework for Citizen Welfare Recommendations</p>
          </div>
        </div>

        <div className="space-y-6 text-xs sm:text-sm text-slate-700 leading-relaxed">
          {/* Research background */}
          <div className="p-4 rounded-2xl bg-blue-50/70 border border-blue-200 text-blue-950">
            <h4 className="font-bold flex items-center gap-1.5 mb-1.5 text-blue-900">
              <BookOpen className="w-4 h-4 text-blue-700" />
              <span>Research Foundation</span>
            </h4>
            <p className="text-xs leading-relaxed">
              Based on the research paper <em>“BenefitBridge AI: A Multi-Agent RAG Framework for Personalized Government Welfare Scheme Recommendation”</em> (Anna University) and the base paper <em>“AI Enabled System for Simplified Access to Government Schemes for All Citizens.”</em>
            </p>
          </div>

          {/* 4 Agents */}
          <div>
            <h4 className="font-bold text-slate-900 uppercase tracking-wider text-xs mb-3">
              The Four-Agent Collaborative Architecture
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                <span className="font-bold text-slate-900 block text-xs mb-1">1. Profile Collector Agent</span>
                <p className="text-xs text-slate-600">
                  Conducts an adaptive interview, extracts citizen demographic and socioeconomic details, and clarifies missing eligibility attributes.
                </p>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                <span className="font-bold text-slate-900 block text-xs mb-1">2. Eligibility Matcher Agent</span>
                <p className="text-xs text-slate-600">
                  Executes explicit deterministic rules (age, income ceiling, state, gender, category) alongside SentenceTransformers ChromaDB vector retrieval.
                </p>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                <span className="font-bold text-slate-900 block text-xs mb-1">3. Scheme Explainer Agent</span>
                <p className="text-xs text-slate-600">
                  Grounds explanations strictly in retrieved official scheme documents without hallucinating benefit amounts, requirements, or URLs.
                </p>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                <span className="font-bold text-slate-900 block text-xs mb-1">4. Language Simplifier Agent</span>
                <p className="text-xs text-slate-600">
                  Simplifies complex bureaucratic terminology into plain, accessible Indian languages (Tamil, Hindi, Telugu, Kannada, English, etc.).
                </p>
              </div>
            </div>
          </div>

          {/* Disclaimer & Limitations */}
          <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-950">
            <h4 className="font-bold flex items-center gap-1.5 mb-1 text-amber-900 text-xs">
              <AlertCircle className="w-4 h-4 text-amber-600" />
              <span>Responsible AI Notice & Limitations</span>
            </h4>
            <p className="text-xs leading-relaxed">
              This system provides <strong>decision-support and informational discovery only</strong>. Final eligibility confirmation and disbursement are exclusively determined by the competent government authority upon physical document verification. BenefitBridge AI does not submit official applications or store private credentials.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
