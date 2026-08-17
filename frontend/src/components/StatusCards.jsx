import React from 'react';
import { AlertCircle, AlertTriangle, ShieldAlert, RefreshCw, Info, ServerCrash } from 'lucide-react';

export default function StatusCards({ response, onRetry }) {
  if (!response) return null;

  // 1. NO CONTEXT STATE
  if (response.grounding_status === 'NO_CONTEXT') {
    return (
      <div className="w-full mb-6 glass-card p-5 border border-sky-500/30 bg-sky-950/20 text-sky-200 animate-fadeIn">
        <div className="flex items-center gap-2.5 mb-2 font-mono font-bold text-sm text-sky-400">
          <Info className="w-4 h-4 shrink-0" />
          <span>INSUFFICIENT CONTEXT</span>
        </div>
        <p className="text-sm font-medium leading-relaxed mb-2 text-slate-200">
          I couldn't find enough information in the available knowledge base to answer this question.
        </p>
        <p className="text-xs text-sky-300/80 font-mono">
          Try asking something related to the available content in MS MARCO-XI.
        </p>
      </div>
    );
  }

  // 2. UNSAFE QUERY BLOCKED STATE
  if (response.grounding_status === 'UNSAFE_QUERY' || response.grounding_status === 'UNSAFE' || response.errorType === 'UNSAFE') {
    return (
      <div className="w-full mb-6 glass-card p-5 border border-amber-500/40 bg-amber-950/30 text-amber-200 animate-fadeIn">
        <div className="flex items-center gap-2.5 mb-2 font-mono font-bold text-sm text-amber-400">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>REQUEST BLOCKED</span>
        </div>
        <p className="text-sm font-medium leading-relaxed text-slate-200">
          Your request could not be processed because it does not meet the system's safety requirements.
        </p>
      </div>
    );
  }

  // 3. RATE LIMITED (HTTP 429)
  if (response.errorType === 'RATE_LIMITED' || response.grounding_status === 'PROVIDER_TIMEOUT') {
    return (
      <div className="w-full mb-6 glass-card p-5 border border-rose-500/40 bg-rose-950/30 text-rose-200 animate-fadeIn">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2.5 font-mono font-bold text-sm text-rose-400">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>AI SERVICE TEMPORARILY BUSY</span>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-3 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-xs font-mono font-semibold text-rose-100 flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          )}
        </div>
        <p className="text-sm font-medium leading-relaxed text-slate-200">
          The AI service is currently handling too many requests. Please try again shortly.
        </p>
      </div>
    );
  }

  // 4. QUOTA / USAGE LIMIT REACHED
  if (response.errorType === 'QUOTA_EXHAUSTED') {
    return (
      <div className="w-full mb-6 glass-card p-5 border border-rose-500/40 bg-rose-950/30 text-rose-200 animate-fadeIn">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2.5 font-mono font-bold text-sm text-rose-400">
            <ServerCrash className="w-4 h-4 shrink-0" />
            <span>AI USAGE LIMIT REACHED</span>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-3 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-xs font-mono font-semibold text-rose-100 flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Later</span>
            </button>
          )}
        </div>
        <p className="text-sm font-medium leading-relaxed text-slate-200">
          The AI service has reached its current usage limit. Please try again later.
        </p>
      </div>
    );
  }

  // 5. GENERIC PROVIDER / NETWORK ERROR
  if (response.errorType === 'PROVIDER_ERROR' || response.errorType === 'NETWORK_ERROR') {
    return (
      <div className="w-full mb-6 glass-card p-5 border border-rose-500/40 bg-rose-950/30 text-rose-200 animate-fadeIn">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2.5 font-mono font-bold text-sm text-rose-400">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>AI SERVICE UNAVAILABLE</span>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-3 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-xs font-mono font-semibold text-rose-100 flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          )}
        </div>
        <p className="text-sm font-medium leading-relaxed text-slate-200">
          {response.message || 'The AI service is temporarily unavailable. Please try again later.'}
        </p>
      </div>
    );
  }

  return null;
}
