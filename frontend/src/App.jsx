import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import LanguageSelector from './components/LanguageSelector';
import MainQueryBox from './components/MainQueryBox';
import ProcessingPipeline from './components/ProcessingPipeline';
import AnswerCard from './components/AnswerCard';
import SourcesAccordion from './components/SourcesAccordion';
import GroundingMeter from './components/GroundingMeter';
import TechnicalDetails from './components/TechnicalDetails';
import StatusCards from './components/StatusCards';
import RecentQuestions, { saveRecentQuestion } from './components/RecentQuestions';
import HowItWorks from './components/HowItWorks';
import AboutModal from './components/AboutModal';
import Footer from './components/Footer';
import { checkBackendHealth, sendAskQuestion } from './services/api';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function App() {
  const [isOnline, setIsOnline] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState('auto');
  const [query, setQuery] = useState('');
  
  // Request State
  const [isLoading, setIsLoading] = useState(false);
  const [isVoiceRequest, setIsVoiceRequest] = useState(false);
  const [response, setResponse] = useState(null);
  
  // TELEMETRY RULE: Strictly request-scoped STT latency (null for text queries)
  const [sttLatencyMs, setSttLatencyMs] = useState(null);
  
  // About Modal
  const [isAboutOpen, setIsAboutOpen] = useState(false);

  // Check health on initial load and poll periodically
  useEffect(() => {
    checkBackendHealth().then((res) => setIsOnline(res.online));
    const interval = setInterval(() => {
      checkBackendHealth().then((res) => setIsOnline(res.online));
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  // Main Submit Handler
  const handleQuerySubmit = async ({ query: submittedQuery, isVoice, stt_latency_ms, detected_stt_language }) => {
    const finalQuery = submittedQuery || query;
    if (!finalQuery || !finalQuery.trim()) return;

    // Save to local recent history
    saveRecentQuestion(finalQuery);

    // CRITICAL TELEMETRY RULE: Reset all request telemetry before execution!
    setIsLoading(true);
    setResponse(null);
    setIsVoiceRequest(Boolean(isVoice));
    
    // Reset STT latency: Only assign if voice request, else strictly null!
    if (isVoice && stt_latency_ms) {
      setSttLatencyMs(stt_latency_ms);
    } else {
      setSttLatencyMs(null);
    }

    try {
      const data = await sendAskQuestion({
        query: finalQuery,
        top_k: 3,
        language_filter: selectedLanguage !== 'auto' ? selectedLanguage : null,
        preferred_answer_language: selectedLanguage !== 'auto' ? selectedLanguage : null
      });

      // Preserve detected STT language if provided
      if (detected_stt_language && !data.detected_language) {
        data.detected_language = detected_stt_language;
      }

      setResponse(data);
      setIsOnline(true);
    } catch (err) {
      console.error('Ask API Exception:', err);
      setResponse({
        errorType: 'PROVIDER_ERROR',
        message: 'Unable to process request. Please check backend connection.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectRecentQuestion = (recentQuery) => {
    setQuery(recentQuery);
    handleQuerySubmit({ query: recentQuery, isVoice: false });
  };

  // Determine detected language for selector badge
  const detectedLangCode = response?.answer_language || response?.detected_language;

  return (
    <div className="min-h-screen flex flex-col justify-between bg-[#050816] text-slate-100 font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      
      {/* Sticky Header */}
      <Header isOnline={isOnline} onOpenAbout={() => setIsAboutOpen(true)} />

      {/* Main Content Area */}
      <main className="page-container py-6 flex-1">
        
        {/* Offline Banner if Backend is down */}
        {!isOnline && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-950/40 border border-rose-500/30 flex items-center justify-between gap-3 text-xs text-rose-300 font-mono animate-fadeIn">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>SYSTEM OFFLINE: Backend FastAPI server unavailable at http://localhost:8000</span>
            </div>
            <button
              onClick={() => checkBackendHealth().then((res) => setIsOnline(res.online))}
              className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 font-semibold flex items-center gap-1.5 shrink-0 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry
            </button>
          </div>
        )}

        {/* Hero Section */}
        <Hero />

        {/* Language Control */}
        <div className="max-w-3xl mx-auto">
          <LanguageSelector
            selectedLanguage={selectedLanguage}
            onChangeLanguage={setSelectedLanguage}
            detectedLanguage={detectedLangCode}
          />

          {/* Main Query Input Box */}
          <MainQueryBox
            query={query}
            setQuery={setQuery}
            onSubmit={handleQuerySubmit}
            isLoading={isLoading}
            selectedLanguage={selectedLanguage}
          />

          {/* Compact Progress Pipeline State */}
          <ProcessingPipeline isLoading={isLoading} isVoice={isVoiceRequest} />
        </div>

        {/* Results Area (Responsive 2-Column Desktop Grid / Single Column Mobile) */}
        {response && !isLoading && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-8 items-start">
            
            {/* LEFT / MAIN COLUMN (8 cols desktop) */}
            <div className="lg:col-span-8 space-y-6">
              
              {/* User Question & AI Answer */}
              {response.answer && (
                <AnswerCard response={response} query={query} />
              )}

              {/* Sources Accordion (Rendered ONLY if sources > 0) */}
              {response.sources && response.sources.length > 0 && (
                <SourcesAccordion sources={response.sources} />
              )}

              {/* Grounding Meter */}
              {response.grounding_status && response.grounding_status !== 'NO_CONTEXT' && (
                <GroundingMeter status={response.grounding_status} score={response.grounding_score} />
              )}

              {/* Special Status Cards (NO_CONTEXT, UNSAFE, RATE_LIMITED, PROVIDER_ERROR) */}
              <StatusCards
                response={response}
                onRetry={() => handleQuerySubmit({ query, isVoice: isVoiceRequest })}
              />

            </div>

            {/* RIGHT / SECONDARY COLUMN (4 cols desktop) */}
            <div className="lg:col-span-4 space-y-6">
              
              {/* Technical Details & Latency Breakdown */}
              <TechnicalDetails response={response} sttLatency={sttLatencyMs} />

              {/* Recent Questions */}
              <RecentQuestions
                onSelectQuestion={handleSelectRecentQuestion}
                activeQuery={query}
              />

            </div>

          </div>
        )}

        {/* If no response yet, show Recent Questions in central area */}
        {!response && !isLoading && (
          <div className="max-w-3xl mx-auto mt-6">
            <RecentQuestions
              onSelectQuestion={handleSelectRecentQuestion}
              activeQuery={query}
            />
          </div>
        )}

        {/* LOWER-PAGE ARCHITECTURE SECTION (Hidden from initial viewport, scroll down required) */}
        <HowItWorks />

      </main>

      {/* About Modal */}
      <AboutModal isOpen={isAboutOpen} onClose={() => setIsAboutOpen(false)} />

      {/* Footer */}
      <Footer />

    </div>
  );
}
