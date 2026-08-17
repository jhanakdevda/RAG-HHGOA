import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import LanguageSelector from './components/LanguageSelector';
import MainQueryBox from './components/MainQueryBox';
import AnswerCard from './components/AnswerCard';
import SourcesAccordion from './components/SourcesAccordion';
import GroundingMeter from './components/GroundingMeter';
import TechnicalDetails from './components/TechnicalDetails';
import StatusCards from './components/StatusCards';
import RecentQuestions, { saveRecentQuestion } from './components/RecentQuestions';
import HowItWorks from './components/HowItWorks';
import AboutSection from './components/AboutSection';
import AboutModal from './components/AboutModal';
import Footer from './components/Footer';
import { checkBackendHealth, sendAskQuestion } from './services/api';
import { RefreshCw } from 'lucide-react';

export default function App() {
  const [isOnline, setIsOnline] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState('auto');
  const [query, setQuery] = useState('');
  
  // Request State
  const [isLoading, setIsLoading] = useState(false);
  const [isVoiceRequest, setIsVoiceRequest] = useState(false);
  const [response, setResponse] = useState(null);
  
  // Request-scoped STT latency
  const [sttLatencyMs, setSttLatencyMs] = useState(null);
  
  // About Modal
  const [isAboutOpen, setIsAboutOpen] = useState(false);

  // How It Works Toggle State (HIDDEN BY DEFAULT)
  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState(false);

  const handleToggleHowItWorks = () => {
    setIsHowItWorksOpen(prev => {
      const nextState = !prev;
      if (nextState) {
        setTimeout(() => {
          const el = document.getElementById('how-it-works');
          if (el) el.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
      return nextState;
    });
  };

  useEffect(() => {
    checkBackendHealth().then((res) => setIsOnline(res.online));
    const interval = setInterval(() => {
      checkBackendHealth().then((res) => setIsOnline(res.online));
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleQuerySubmit = async ({ query: submittedQuery, isVoice, stt_latency_ms, detected_stt_language }) => {
    const finalQuery = submittedQuery || query;
    if (!finalQuery || !finalQuery.trim()) return;

    saveRecentQuestion(finalQuery);

    setIsLoading(true);
    setResponse(null);
    setIsVoiceRequest(Boolean(isVoice));
    
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

  const detectedLangCode = response?.answer_language || response?.detected_language;

  return (
    <div className="min-h-screen flex flex-col justify-between bg-[#070a14] text-slate-100 font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      
      {/* 1. Header */}
      <Header
        isOnline={isOnline}
        onOpenAbout={() => setIsAboutOpen(true)}
        isHowItWorksOpen={isHowItWorksOpen}
        onToggleHowItWorks={handleToggleHowItWorks}
      />

      {/* Main Long Scrollable Page Content */}
      <main className="w-full flex-1">
        
        {/* Unobtrusive Offline Banner near top */}
        {!isOnline && (
          <div className="max-w-4xl mx-auto px-4 mt-4">
            <div className="py-2 px-3 rounded-lg bg-rose-950/30 border border-rose-500/20 flex items-center justify-between text-xs text-rose-300 font-mono animate-fadeIn">
              <div className="flex items-center gap-2">
                <span className="dot-offline" />
                <span>Backend offline — Start FastAPI to enable live RAG</span>
              </div>
              <button
                onClick={() => checkBackendHealth().then((res) => setIsOnline(res.online))}
                className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 text-[11px] flex items-center gap-1 transition-colors"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Retry</span>
              </button>
            </div>
          </div>
        )}

        {/* 2. Hero Section */}
        <Hero />

        {/* 3. Query / Voice Area */}
        <section className="max-w-3xl mx-auto px-4 mb-12">
          <LanguageSelector
            selectedLanguage={selectedLanguage}
            onChangeLanguage={setSelectedLanguage}
            detectedLanguage={detectedLangCode}
          />

          <MainQueryBox
            query={query}
            setQuery={setQuery}
            onSubmit={handleQuerySubmit}
            isLoading={isLoading}
            selectedLanguage={selectedLanguage}
          />
        </section>

        {/* 4. Answer Results Section */}
        {response && !isLoading && (
          <section className="max-w-4xl mx-auto px-4 mb-16 space-y-4 animate-fadeIn">
            {/* User Question & AI Answer */}
            {response.answer && (
              <AnswerCard response={response} query={query} />
            )}

            {/* Collapsible Sources */}
            {response.sources && response.sources.length > 0 && (
              <SourcesAccordion sources={response.sources} />
            )}

            {/* Grounding Status Meter */}
            {response.grounding_status && response.grounding_status !== 'NO_CONTEXT' && (
              <GroundingMeter status={response.grounding_status} score={response.grounding_score} />
            )}

            {/* Special Fail-Fast / Error Status Cards */}
            <StatusCards
              response={response}
              onRetry={() => handleQuerySubmit({ query, isVoice: isVoiceRequest })}
            />

            {/* Collapsible Technical Details */}
            <TechnicalDetails response={response} sttLatency={sttLatencyMs} />
          </section>
        )}

        {/* 5. Recent & Sample Questions */}
        <section className="max-w-4xl mx-auto px-4 mb-16">
          <RecentQuestions
            onSelectQuestion={handleSelectRecentQuestion}
            activeQuery={query}
          />
        </section>

        {/* 6. How It Works (Hidden by default, expands on demand) */}
        <section id="how-it-works" className="max-w-5xl mx-auto px-4">
          <HowItWorks
            isOpen={isHowItWorksOpen}
            onToggle={handleToggleHowItWorks}
          />
        </section>

        {/* 7. About / Project Overview Section */}
        <section className="max-w-4xl mx-auto px-4 mb-16">
          <AboutSection />
        </section>

      </main>

      {/* About Modal Dialog */}
      <AboutModal isOpen={isAboutOpen} onClose={() => setIsAboutOpen(false)} />

      {/* 8. Footer */}
      <Footer />

    </div>
  );
}
