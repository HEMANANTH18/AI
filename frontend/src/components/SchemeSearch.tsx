import React, { useState, useEffect } from "react";
import { searchSchemes } from "../api";
import { getTranslation } from "../i18n/translations";
import { Search, ExternalLink, ChevronRight, ChevronLeft } from "lucide-react";

interface SchemeSearchProps {
  selectedLanguage: string;
  onOpenDetail: (schemeId: string) => void;
}

export const SchemeSearch: React.FC<SchemeSearchProps> = ({ selectedLanguage, onOpenDetail }) => {
  const t = getTranslation(selectedLanguage);
  const [query, setQuery] = useState("");
  const [selectedState, setSelectedState] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedBenefitType, setSelectedBenefitType] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(false);

  const pageSize = 12;

  const loadData = async (offset = 0) => {
    setLoading(true);
    try {
      const data = await searchSchemes({
        query: query.trim() || undefined,
        state: selectedState || undefined,
        category: selectedCategory || undefined,
        benefit_type: selectedBenefitType || undefined,
        limit: pageSize,
        offset: offset,
      });
      setResults(data.results || []);
      setTotal(data.total || 0);
      setPage(Math.floor(offset / pageSize));
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(0);
  }, [selectedState, selectedCategory, selectedBenefitType]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData(0);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Title & Filter bar */}
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-2">
          {t.searchTitle}
        </h1>
        <p className="text-sm text-slate-600 max-w-2xl mb-6">
          {t.searchSubtitle}
        </p>

        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="flex gap-2 max-w-2xl mb-4">
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-3 pointer-events-none" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t.searchPlaceholder}
              className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-semibold text-sm transition-colors shadow-xs cursor-pointer"
          >
            {t.searchBtn}
          </button>
        </form>

        {/* Filters Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-2xl">
          {/* State filter */}
          <div>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="w-full text-xs sm:text-sm p-2 rounded-xl border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{t.allStates}</option>
              <option value="Tamil Nadu">Tamil Nadu (தமிழ்நாடு)</option>
              <option value="Gujarat">Gujarat (ગુજરાત)</option>
              <option value="Uttarakhand">Uttarakhand (उत्तराखंड)</option>
              <option value="Madhya Pradesh">Madhya Pradesh (मध्य प्रदेश)</option>
              <option value="Puducherry">Puducherry (புதுச்சேரி)</option>
              <option value="Goa">Goa (गोवा)</option>
              <option value="Haryana">Haryana (हरियाणा)</option>
              <option value="Rajasthan">Rajasthan (राजस्थान)</option>
              <option value="Bihar">Bihar (बिहार)</option>
              <option value="Andhra Pradesh">Andhra Pradesh (ఆంధ్రప్రదేశ్)</option>
              <option value="Maharashtra">Maharashtra (महाराष्ट्र)</option>
              <option value="Karnataka">Karnataka (ಕರ್ನಾಟಕ)</option>
              <option value="Kerala">Kerala (കേരളം)</option>
            </select>
          </div>

          {/* Category filter */}
          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full text-xs sm:text-sm p-2 rounded-xl border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{t.allCategories}</option>
              <option value="Agriculture">Agriculture & Rural</option>
              <option value="Education">Education & Learning</option>
              <option value="Social welfare">Social Welfare & Empowerment</option>
              <option value="Business">Business & Entrepreneurship</option>
              <option value="Health">Health & Wellness</option>
              <option value="Skills">Skills & Employment</option>
              <option value="Banking">Banking & Insurance</option>
            </select>
          </div>

          {/* Benefit type filter */}
          <div>
            <select
              value={selectedBenefitType}
              onChange={(e) => setSelectedBenefitType(e.target.value)}
              className="w-full text-xs sm:text-sm p-2 rounded-xl border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{t.allBenefits}</option>
              <option value="Cash">Cash Financial Transfer</option>
              <option value="In Kind">In Kind Services / Goods</option>
              <option value="Composite">Composite</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3 mb-6">
        <span className="text-sm font-semibold text-slate-700">
          {t.showingResults} {results.length} of {total} schemes
        </span>
      </div>

      {/* Schemes Grid */}
      {loading ? (
        <div className="py-24 text-center text-slate-500">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-sm">Filtering schemes across registry...</p>
        </div>
      ) : results.length === 0 ? (
        <div className="py-20 text-center bg-white rounded-3xl border border-slate-200 p-8">
          <p className="text-base font-semibold text-slate-800 mb-1">No matching schemes found</p>
          <p className="text-xs text-slate-500">Try clearing the filters or searching with different terms.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results.map((s) => (
            <div
              key={s.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center gap-1.5 mb-2.5">
                  <span className="px-2 py-0.5 rounded-md text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100">
                    {s.level}
                  </span>
                  {s.state && s.state !== "All India" && (
                    <span className="px-2 py-0.5 rounded-md text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-100">
                      {s.state}
                    </span>
                  )}
                  <span className="px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-600">
                    {s.benefit_type}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 leading-snug mb-2 line-clamp-2">
                  {s.name}
                </h3>

                <p className="text-xs text-slate-600 line-clamp-3 mb-4 leading-relaxed">
                  {s.brief_description}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <button
                  onClick={() => onOpenDetail(s.id)}
                  className="flex items-center space-x-1 text-xs font-semibold text-blue-700 hover:text-blue-800 cursor-pointer"
                >
                  <span>{t.viewGuidelines}</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>

                {s.official_url && (
                  <a
                    href={s.official_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-1 text-xs text-slate-500 hover:text-slate-800"
                  >
                    <span>{t.officialPortal}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {total > pageSize && (
        <div className="flex items-center justify-center gap-3 mt-10">
          <button
            onClick={() => loadData((page - 1) * pageSize)}
            disabled={page === 0}
            className="flex items-center space-x-1 px-4 py-2 rounded-xl border border-slate-300 text-xs font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>{t.prevPage}</span>
          </button>
          <span className="text-xs font-medium text-slate-600">
            Page {page + 1} of {Math.ceil(total / pageSize)}
          </span>
          <button
            onClick={() => loadData((page + 1) * pageSize)}
            disabled={(page + 1) * pageSize >= total}
            className="flex items-center space-x-1 px-4 py-2 rounded-xl border border-slate-300 text-xs font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <span>{t.nextPage}</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};
