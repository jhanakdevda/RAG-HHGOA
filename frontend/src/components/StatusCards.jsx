import React from 'react';
import { Search, ShieldAlert, AlertTriangle, RefreshCw, AlertCircle } from 'lucide-react';

export default function StatusCards({ response, onRetry }) {
  if (!response) return null;

  // 1. NO CONTEXT STATE (Professional empty state, non-alarming)
  if (response.grounding_status === 'NO_CONTEXT') {
    return (
      <div className="w-full mb-6 tech-panel p-6 text-center border border-white/10 bg-[#10151C] animate-fadeIn font-sans">
        <div className="w-10 h-10 rounded-full bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mx-auto mb-3">
          <Search className="w-5 h-5" />
        </div>
        <h3 className="text-sm font-bold text-slate-100 font-mono tracking-wide uppercase mb-1">
          No supporting evidence found
        </h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
          Try asking something related to the indexed knowledge base.
        </p>
      </div>
    );
  }

  // 2. UNSAFE QUERY BLOCKED STATE
  if (response.grounding_status === 'UNSAFE_QUERY' || response.grounding_status === 'UNSAFE' || response.errorType === 'UNSAFE') {
    return (
      <div className="w-full mb-6 tech-panel p-4 border border-amber-500/30 bg-amber-950/20 text-amber-200 animate-fadeIn font-sans">
        <div className="flex items-center gap-2 mb-1 font-mono font-bold text-xs text-amber-400">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>REQUEST BLOCKED BY SAFETY FILTER</span>
        </div>
        <p className="text-xs leading-relaxed text-slate-300">
          This query violates safety guidelines. Please modify your query and try again.
        </p>
      </div>
    );
  }

  // 3. RATE LIMITED (HTTP 429)
  if (response.errorType === 'RATE_LIMITED' || response.grounding_status === 'PROVIDER_TIMEOUT') {
    return (
      <div className="w-full mb-6 tech-panel p-4 border border-rose-500/30 bg-rose-950/20 text-rose-200 animate-fadeIn font-sans">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2 font-mono font-bold text-xs text-rose-400">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>AI SERVICE TEMPORARILY BUSY</span>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-xs font-mono text-rose-200 flex items-center gap-1 transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Retry</span>
            </button>
          )}
        </div>
        <p className="text-xs text-slate-300">
          Groq AI service is currently rate-limited. Please wait a few seconds and try again.
        </p>
      </div>
    );
  }

  // 4. PROVIDER ERROR / QUOTA
  if (response.errorType === 'PROVIDER_ERROR' || response.errorType === 'QUOTA_EXHAUSTED' || response.errorType === 'NETWORK_ERROR') {
    return (
      <div className="w-full mb-6 tech-panel p-4 border border-rose-500/30 bg-rose-950/20 text-rose-200 animate-fadeIn font-sans">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2 font-mono font-bold text-xs text-rose-400">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>AI SERVICE UNAVAILABLE</span>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-xs font-mono text-rose-200 flex items-center gap-1 transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Retry</span>
            </button>
          )}
        </div>
        <p className="text-xs text-slate-300">
          {response.message || 'Unable to connect to AI provider. Please try again later.'}
        </p>
      </div>
    );
  }

  return null;
}
