import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import MainQueryBox from './components/MainQueryBox';
import AnswerCard from './components/AnswerCard';
import SourcesAccordion from './components/SourcesAccordion';
import TechnicalDetails from './components/TechnicalDetails';
import HowItWorksModal from './components/HowItWorksModal';
import AboutModal from './components/AboutModal';
import KnowledgeBackground from './components/KnowledgeBackground';
import { checkBackendHealth, submitQuestion } from './services/api';

export default function App() {
  const [isOnline, setIsOnline] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState('auto');
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [appState, setAppState] = useState('IDLE');
  const [response, setResponse] = useState(null);

  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState(false);
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);

  useEffect(() => {
    const verifyHealth = async () => {
      const res = await checkBackendHealth();
      setIsOnline(res.online);
    };
    verifyHealth();
    const interval = setInterval(verifyHealth, 25000);
    return () => clearInterval(interval);
  }, []);

  const handleQuerySubmit = async ({ query: submittedQuery, isVoice }) => {
    if (!submittedQuery || isLoading) return;

    setIsLoading(true);
    setAppState('RETRIEVING');
    setResponse(null);

    try {
      setTimeout(() => {
        if (isLoading) setAppState('GENERATING');
      }, 700);

      setTimeout(() => {
        if (isLoading) setAppState('VERIFYING');
      }, 1400);

      const preferredLang = selectedLanguage === 'auto' ? null : selectedLanguage;
      const apiRes = await submitQuestion({
        query: submittedQuery,
        preferred_answer_language: preferredLang
      });

      if (apiRes.success && apiRes.data) {
        setResponse(apiRes.data);
        setAppState('ANSWER_COMPLETE');
      } else {
        setResponse({
          answer: apiRes.error_message || 'Could not fetch grounded answer.',
          sources: [],
          grounding_status: 'UNVERIFIED',
          retrieval_latency_ms: 0,
          generation_latency_ms: 0,
          total_latency_ms: 0
        });
        setAppState('IDLE');
      }
    } catch (err) {
      console.error('Submission error:', err);
      setResponse({
        answer: 'Failed to connect to backend service. Please verify server connection.',
        sources: [],
        grounding_status: 'UNVERIFIED',
        retrieval_latency_ms: 0,
        generation_latency_ms: 0,
        total_latency_ms: 0
      });
      setAppState('IDLE');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020108] text-slate-100 flex flex-col font-sans relative selection:bg-pink-500 selection:text-white">
      
      {/* 1. Global Live Sunset Aurora Particle Background */}
      <KnowledgeBackground appState={appState} />

      {/* 2. Header Navigation Bar */}
      <Header
        isOnline={isOnline}
        onToggleHowItWorks={() => setIsHowItWorksOpen(!isHowItWorksOpen)}
      />

      {/* 3. Main Central Portrait Flow Workspace Container */}
      <main className="max-w-4xl w-full mx-auto px-4 sm:px-8 py-10 sm:py-16 flex-1 space-y-12 sm:space-y-16 relative z-10">
        
        {/* Centered Hero Header */}
        <HeroSection />

        {/* Central Voice Mic Console Card with 50% Glass Transparency & Square Voice Mic Block */}
        <MainQueryBox
          query={query}
          setQuery={setQuery}
          onSubmit={handleQuerySubmit}
          isLoading={isLoading}
          selectedLanguage={selectedLanguage}
          onLanguageChange={setSelectedLanguage}
        />

        {/* Dynamic Output Stack (Appears upon answer execution) */}
        {response && (
          <div className="space-y-12 sm:space-y-16 animate-fadeIn">
            {/* Grounded AI Answer Card */}
            <AnswerCard response={response} query={query} />

            {/* Retrieved Knowledge Evidence Stack */}
            <SourcesAccordion sources={response.sources} />

            {/* High-Precision Telemetry HUD Latency Card */}
            <TechnicalDetails response={response} />
          </div>
        )}

      </main>

      {/* Modals & Overlays */}
      <HowItWorksModal
        isOpen={isHowItWorksOpen}
        onClose={() => setIsHowItWorksOpen(false)}
      />

      <AboutModal
        isOpen={isAboutModalOpen}
        onClose={() => setIsAboutModalOpen(false)}
      />

    </div>
  );
}
