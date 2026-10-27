import React, { useState, useRef, useEffect } from "react";
import {
  CitizenProfile,
  MultiAgentWorkflowResponse,
  SimplifiedSchemeOutput,
  SchemeRecommendation,
} from "../types";
import { sendChatMessage, localizeRecommendations } from "../api";
import { SchemeCard } from "./SchemeCard";
import { ProfilePanel } from "./ProfilePanel";
import { getTranslation } from "../i18n/translations";
import { Send, Bot, User, Sparkles, HelpCircle, AlertCircle, Clock } from "lucide-react";

interface Message {
  sender: "user" | "agent";
  text: string;
  timestamp: string;
  suggestedOptions?: string[] | null;
  acknowledgement?: string | null;
  latencies?: Record<string, number>;
}

interface ChatInterfaceProps {
  sessionId: string;
  selectedLanguage: string;
  onOpenSchemeModal: (schemeId: string) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  sessionId,
  selectedLanguage,
  onOpenSchemeModal,
}) => {
  const t = getTranslation(selectedLanguage);

  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "agent",
      text: t.greetingMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      suggestedOptions: [
        "I am a farmer from Tamil Nadu",
        "Student in Gujarat looking for scholarships",
        "Construction worker in Andhra Pradesh",
        "Handloom weaver seeking artisan subsidy",
      ],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<CitizenProfile>({});
  const [profileComplete, setProfileComplete] = useState(false);
  const [recommendations, setRecommendations] = useState<SimplifiedSchemeOutput[]>([]);
  const [rawRecs, setRawRecs] = useState<SchemeRecommendation[]>([]);
  const [latencies, setLatencies] = useState<Record<string, number>>({});

  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Handle dynamic language change
  useEffect(() => {
    const currentT = getTranslation(selectedLanguage);

    // If chat is only the initial greeting, translate greeting message
    setMessages((prev) => {
      if (prev.length === 1 && prev[0].sender === "agent") {
        return [
          {
            ...prev[0],
            text: currentT.greetingMessage,
          },
        ];
      }
      return prev;
    });

    // If active recommendations are displayed, dynamically re-localize them from backend
    if (recommendations.length > 0) {
      const schemeIds = recommendations.map((r) => r.scheme_id);
      localizeRecommendations(sessionId, selectedLanguage, schemeIds)
        .then((localized) => {
          if (localized && localized.length > 0) {
            setRecommendations(localized);
          }
        })
        .catch((err) => {
          console.warn("Failed to re-localize recommendations:", err);
        });
    }
  }, [selectedLanguage]);

  const handleSend = async (messageText?: string) => {
    const textToSend = (messageText || input).trim();
    if (!textToSend || loading) return;

    setInput("");
    const userMsg: Message = {
      sender: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response: MultiAgentWorkflowResponse = await sendChatMessage(
        sessionId,
        textToSend,
        selectedLanguage
      );

      setProfile(response.profile);
      setProfileComplete(response.profile_complete);
      if (response.recommendations && response.recommendations.length > 0) {
        setRecommendations(response.recommendations);
        setRawRecs(response.raw_recommendations || []);
      }
      if (response.meta?.latencies) {
        setLatencies(response.meta.latencies);
      }

      // Construct agent reply
      let replyText = "";
      if (response.acknowledgement_text) {
        replyText += response.acknowledgement_text + " ";
      }
      if (response.clarification_question) {
        replyText += response.clarification_question;
      } else if (response.recommendations.length > 0) {
        replyText += `I've evaluated your profile against our 4,670 government schemes and identified ${response.recommendations.length} matching welfare programs below:`;
      } else {
        replyText += "We couldn't identify verified schemes matching this profile. Please adjust your criteria or specify your occupation and state.";
      }

      const agentMsg: Message = {
        sender: "agent",
        text: replyText.trim(),
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        suggestedOptions: response.suggested_options,
        latencies: response.meta?.latencies,
      };

      setMessages((prev) => [...prev, agentMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: `Error: ${err.message || "Failed to process request"}. Please verify backend server is running.`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (updated: CitizenProfile) => {
    setLoading(true);
    try {
      const summaryMsg = `Updated profile: Age ${updated.age || ""}, State ${updated.state || ""}, Occupation ${updated.occupation || ""}, Income ₹${updated.annual_income || ""}`;
      const response = await sendChatMessage(sessionId, summaryMsg, selectedLanguage, updated);
      setProfile(response.profile);
      setProfileComplete(response.profile_complete);
      if (response.recommendations && response.recommendations.length > 0) {
        setRecommendations(response.recommendations);
        setRawRecs(response.raw_recommendations || []);
      }
      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: `Profile updated successfully! Evaluated ${response.recommendations.length} tailored welfare schemes.`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          latencies: response.meta?.latencies,
        },
      ]);
    } catch (err: any) {
      alert("Failed to update profile: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6">
      {/* Citizen Profile Status Panel */}
      <ProfilePanel
        profile={profile}
        isComplete={profileComplete}
        selectedLanguage={selectedLanguage}
        onUpdateProfile={handleUpdateProfile}
      />

      {/* Main Conversation & Recommendation Container */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Conversational Interview (5 or 6 cols) */}
        <div className="lg:col-span-5 flex flex-col bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden h-[620px]">
          {/* Header */}
          <div className="px-5 py-3.5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="font-bold text-xs sm:text-sm text-slate-800">
                {selectedLanguage === "ta"
                  ? "குடிமக்கள் நேர்காணல்"
                  : selectedLanguage === "hi"
                  ? "नागरिक साक्षात्कार"
                  : selectedLanguage === "te"
                  ? "పౌర ముఖాముఖి"
                  : selectedLanguage === "kn"
                  ? "ನಾಗರಿಕ ಸಂದರ್ಶನ"
                  : selectedLanguage === "ml"
                  ? "പൗര അഭിമുഖം"
                  : selectedLanguage === "bn"
                  ? "নাগরিক সাক্ষাৎকার"
                  : selectedLanguage === "mr"
                  ? "नागरिक मुलाखत"
                  : "Citizen Interview"}
              </span>
            </div>
            {latencies.total_pipeline_ms && (
              <span className="flex items-center text-xs text-slate-500 font-mono">
                <Clock className="w-3 h-3 mr-1" />
                {latencies.total_pipeline_ms} ms
              </span>
            )}
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${m.sender === "user" ? "items-end" : "items-start"}`}
              >
                <div className="flex items-start space-x-2 max-w-[88%]">
                  {m.sender === "agent" && (
                    <div className="w-7 h-7 rounded-full bg-blue-700 flex items-center justify-center text-white flex-shrink-0 mt-0.5 shadow-xs">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}
                  <div
                    className={`p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                      m.sender === "user"
                        ? "bg-blue-600 text-white rounded-tr-xs"
                        : "bg-slate-100 text-slate-800 rounded-tl-xs border border-slate-200/80"
                    }`}
                  >
                    <p>{m.text}</p>
                  </div>
                  {m.sender === "user" && (
                    <div className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center text-white flex-shrink-0 mt-0.5 shadow-xs">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>

                {/* Quick Reply Chips */}
                {m.suggestedOptions && m.suggestedOptions.length > 0 && idx === messages.length - 1 && (
                  <div className="mt-2.5 ml-9 flex flex-wrap gap-1.5 max-w-[85%]">
                    {m.suggestedOptions.map((opt, oIdx) => (
                      <button
                        key={oIdx}
                        onClick={() => handleSend(opt)}
                        disabled={loading}
                        className="text-xs bg-white text-blue-700 hover:bg-blue-50 border border-blue-200 hover:border-blue-400 px-3 py-1.5 rounded-full font-medium transition-all shadow-2xs"
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-center space-x-2 text-slate-500 text-xs">
                <div className="w-6 h-6 rounded-full bg-blue-700 flex items-center justify-center text-white">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="bg-slate-100 px-4 py-2 rounded-2xl border border-slate-200 flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce"></div>
                  <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-2 h-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.4s]"></div>
                  <span className="text-xs font-medium text-slate-600 ml-1">{t.evaluatingText}</span>
                </div>
              </div>
            )}
            <div ref={chatBottomRef} />
          </div>

          {/* Chat Input Bar */}
          <div className="p-3 bg-slate-50 border-t border-slate-200">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center space-x-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={t.chatPlaceholder}
                disabled={loading}
                className="flex-1 bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="p-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white disabled:opacity-40 transition-colors shadow-xs"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Recommendations (6 or 7 cols) */}
        <div className="lg:col-span-7 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-500" />
                <span>{t.recsHeader}</span>
              </h2>
              <p className="text-xs text-slate-500">
                {t.recsSubheader}
              </p>
            </div>
            {recommendations.length > 0 && (
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                {recommendations.length} {t.matchesFound}
              </span>
            )}
          </div>

          {recommendations.length === 0 ? (
            <div className="bg-white rounded-3xl border border-dashed border-slate-300 p-8 text-center flex flex-col items-center justify-center h-[550px]">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
                <Sparkles className="w-7 h-7" />
              </div>
              <h3 className="font-bold text-slate-800 text-base mb-1">{t.noRecsTitle}</h3>
              <p className="text-xs text-slate-500 max-w-sm mb-4 leading-relaxed">
                {t.noRecsDesc}
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                <button
                  onClick={() => handleSend("I am a 35 year old farmer living in Tamil Nadu with income 180000")}
                  className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg transition-colors"
                >
                  {t.exampleFarmer}
                </button>
                <button
                  onClick={() => handleSend("I am a 20 year old ST student from Gujarat looking for scholarships")}
                  className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg transition-colors"
                >
                  {t.exampleStudent}
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4 overflow-y-auto max-h-[560px] pr-1">
              {recommendations.map((rec) => {
                const raw = rawRecs.find((r) => r.scheme_id === rec.scheme_id);
                return (
                  <SchemeCard
                    key={rec.scheme_id}
                    scheme={rec}
                    rawDetails={raw}
                    selectedLanguage={selectedLanguage}
                    onOpenDetail={onOpenSchemeModal}
                  />
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
