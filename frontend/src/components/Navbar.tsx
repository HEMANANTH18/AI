import React from "react";
import { SupportedLanguage } from "../types";
import { getTranslation } from "../i18n/translations";
import { Landmark, Languages, RotateCcw, Database, Info, Search, MessageSquare } from "lucide-react";

interface NavbarProps {
  currentTab: "chat" | "search";
  setCurrentTab: (tab: "chat" | "search") => void;
  languages: SupportedLanguage[];
  selectedLanguage: string;
  onSelectLanguage: (lang: string) => void;
  onReset: () => void;
  onOpenDatasetModal: () => void;
  onOpenAboutModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  languages,
  selectedLanguage,
  onSelectLanguage,
  onReset,
  onOpenDatasetModal,
  onOpenAboutModal,
}) => {
  const t = getTranslation(selectedLanguage);

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab("chat")}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white shadow-md">
            <Landmark className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight text-slate-900">{t.brandTitle}</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                Multi-Agent RAG
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">{t.brandSubtitle}</p>
          </div>
        </div>

        {/* Center Nav tabs */}
        <div className="hidden md:flex items-center space-x-1 bg-slate-100 p-1 rounded-xl">
          <button
            onClick={() => setCurrentTab("chat")}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentTab === "chat"
                ? "bg-white text-blue-700 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>{t.tabChat}</span>
          </button>
          <button
            onClick={() => setCurrentTab("search")}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentTab === "search"
                ? "bg-white text-blue-700 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Search className="w-4 h-4" />
            <span>{t.tabSearch}</span>
          </button>
        </div>

        {/* Right actions: Language selector, Reset, Dataset info, About */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Language dropdown */}
          <div className="relative flex items-center">
            <Languages className="w-4 h-4 text-slate-500 absolute left-2.5 pointer-events-none" />
            <select
              value={selectedLanguage}
              onChange={(e) => onSelectLanguage(e.target.value)}
              className="pl-8 pr-4 py-1.5 bg-slate-50 border border-slate-300 rounded-lg text-xs sm:text-sm font-medium text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
              {languages.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.native} ({l.name})
                </option>
              ))}
            </select>
          </div>

          {/* Reset session button */}
          <button
            onClick={onReset}
            title={t.resetTooltip}
            className="p-2 text-slate-600 hover:text-amber-700 hover:bg-amber-50 rounded-lg border border-slate-200 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          {/* Dataset Status button */}
          <button
            onClick={onOpenDatasetModal}
            title={t.datasetTooltip}
            className="p-2 text-slate-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg border border-slate-200 transition-colors"
          >
            <Database className="w-4 h-4" />
          </button>

          {/* About / Limitations modal */}
          <button
            onClick={onOpenAboutModal}
            title={t.aboutTooltip}
            className="p-2 text-slate-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg border border-slate-200 transition-colors"
          >
            <Info className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
