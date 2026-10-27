import React, { useState, useEffect } from "react";
import { SupportedLanguage } from "./types";
import { fetchSupportedLanguages, resetSession } from "./api";
import { Navbar } from "./components/Navbar";
import { ChatInterface } from "./components/ChatInterface";
import { SchemeSearch } from "./components/SchemeSearch";
import { SchemeModal } from "./components/SchemeModal";
import { DatasetStatusModal } from "./components/DatasetStatusModal";
import { AboutModal } from "./components/AboutModal";

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<"chat" | "search">("chat");
  const [languages, setLanguages] = useState<SupportedLanguage[]>([
    { code: "en", name: "English", native: "English" },
    { code: "ta", name: "Tamil", native: "தமிழ்" },
    { code: "hi", name: "Hindi", native: "हिन्दी" },
  ]);
  const [selectedLanguage, setSelectedLanguage] = useState<string>("en");
  const [sessionId, setSessionId] = useState<string>(
    () => "bb-session-" + Math.random().toString(36).substring(2, 9)
  );

  // Modals state
  const [modalSchemeId, setModalSchemeId] = useState<string | null>(null);
  const [isDatasetModalOpen, setIsDatasetModalOpen] = useState(false);
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);

  useEffect(() => {
    fetchSupportedLanguages()
      .then((data) => {
        if (data && data.length > 0) setLanguages(data);
      })
      .catch((err) => console.warn("Could not load languages list:", err));
  }, []);

  const handleReset = async () => {
    if (window.confirm("Start a new conversation and reset citizen profile?")) {
      try {
        await resetSession(sessionId);
      } catch (e) {
        console.warn(e);
      }
      const newSession = "bb-session-" + Math.random().toString(36).substring(2, 9);
      setSessionId(newSession);
      window.location.reload();
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-900 selection:bg-blue-100 selection:text-blue-900">
      {/* Top Navigation */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        languages={languages}
        selectedLanguage={selectedLanguage}
        onSelectLanguage={setSelectedLanguage}
        onReset={handleReset}
        onOpenDatasetModal={() => setIsDatasetModalOpen(true)}
        onOpenAboutModal={() => setIsAboutModalOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        {currentTab === "chat" ? (
          <ChatInterface
            sessionId={sessionId}
            selectedLanguage={selectedLanguage}
            onOpenSchemeModal={(id) => setModalSchemeId(id)}
          />
        ) : (
          <SchemeSearch
            selectedLanguage={selectedLanguage}
            onOpenDetail={(id) => setModalSchemeId(id)}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>© 2026 BenefitBridge AI • Anna University Student Research Project</p>
          <p className="text-slate-400">
            Authoritative Knowledge Base: 4,670 Schemes from <strong>myScheme.gov.in</strong>
          </p>
        </div>
      </footer>

      {/* Modals */}
      <SchemeModal
        schemeId={modalSchemeId}
        onClose={() => setModalSchemeId(null)}
      />
      <DatasetStatusModal
        isOpen={isDatasetModalOpen}
        onClose={() => setIsDatasetModalOpen(false)}
      />
      <AboutModal
        isOpen={isAboutModalOpen}
        onClose={() => setIsAboutModalOpen(false)}
      />
    </div>
  );
};
export default App;
