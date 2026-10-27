import React from "react";
import { SimplifiedSchemeOutput, SchemeRecommendation } from "../types";
import { getTranslation } from "../i18n/translations";
import { ExternalLink, CheckCircle2, AlertCircle, HelpCircle, Gift, ChevronRight } from "lucide-react";

interface SchemeCardProps {
  scheme: SimplifiedSchemeOutput;
  rawDetails?: SchemeRecommendation;
  selectedLanguage: string;
  onOpenDetail: (schemeId: string) => void;
}

export const SchemeCard: React.FC<SchemeCardProps> = ({
  scheme,
  rawDetails,
  selectedLanguage,
  onOpenDetail,
}) => {
  const t = getTranslation(selectedLanguage);
  const matchScore = rawDetails ? Math.round(rawDetails.match_score * 100) : 85;
  const status = rawDetails?.eligibility_status || "potentially_eligible";

  const getStatusBadge = () => {
    switch (status) {
      case "eligible_based_on_available_rules":
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
            {t.statusEligible}
          </span>
        );
      case "potentially_eligible":
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-300">
            <HelpCircle className="w-3.5 h-3.5 mr-1" />
            {t.statusPotential}
          </span>
        );
      case "not_eligible_based_on_known_rules":
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-300">
            <AlertCircle className="w-3.5 h-3.5 mr-1" />
            {t.statusMismatch}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300">
            <HelpCircle className="w-3.5 h-3.5 mr-1" />
            {t.statusVerify}
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all p-5 flex flex-col justify-between">
      <div>
        {/* Top Badges */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="flex flex-wrap items-center gap-1.5">
            {getStatusBadge()}
            {rawDetails?.level && (
              <span className="px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700">
                {rawDetails.level}
              </span>
            )}
            {rawDetails?.state && rawDetails.state !== "All India" && (
              <span className="px-2 py-0.5 rounded-md text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100">
                {rawDetails.state}
              </span>
            )}
          </div>
          {/* Match Score */}
          <div className="flex items-center space-x-1 bg-slate-50 px-2 py-1 rounded-lg border border-slate-200 text-xs font-bold text-slate-800">
            <span>{t.matchScore}:</span>
            <span className={matchScore >= 75 ? "text-emerald-700" : "text-blue-700"}>
              {matchScore}%
            </span>
          </div>
        </div>

        {/* Scheme Name */}
        <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-snug mb-1">
          {scheme.localized_scheme_name || scheme.scheme_id}
        </h3>
        {rawDetails?.scheme_name && rawDetails.scheme_name !== scheme.localized_scheme_name && (
          <p className="text-xs text-slate-500 mb-2 italic">{rawDetails.scheme_name}</p>
        )}

        {/* Summary */}
        <p className="text-xs sm:text-sm text-slate-600 line-clamp-3 mb-4">
          {scheme.simple_explanation || scheme.eligibility_summary}
        </p>

        {/* Highlights */}
        {scheme.benefits && scheme.benefits.length > 0 && (
          <div className="mb-3 bg-blue-50/60 rounded-xl p-3 border border-blue-100/70">
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-blue-900 mb-1">
              <Gift className="w-3.5 h-3.5 text-blue-600" />
              <span>{t.keyBenefits}</span>
            </div>
            <p className="text-xs text-blue-950 line-clamp-2">
              {scheme.benefits[0]}
            </p>
          </div>
        )}

        {/* Matched reasons pills */}
        {rawDetails?.matched_reasons && rawDetails.matched_reasons.length > 0 && (
          <div className="mb-4">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              {t.alignment}
            </span>
            <div className="flex flex-wrap gap-1">
              {rawDetails.matched_reasons.slice(0, 2).map((r, i) => (
                <span key={i} className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md">
                  ✓ {r}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2 mt-2">
        <button
          onClick={() => onOpenDetail(scheme.scheme_id)}
          className="flex items-center space-x-1.5 text-xs font-semibold text-blue-700 hover:text-blue-800 hover:bg-blue-50 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
        >
          <span>{t.viewGuidelines}</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>

        {scheme.official_application_url && (
          <a
            href={scheme.official_application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 text-xs font-medium text-slate-600 hover:text-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors"
          >
            <span>{t.officialPortal}</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </div>
  );
};
