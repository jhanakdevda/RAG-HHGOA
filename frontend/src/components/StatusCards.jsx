import React from 'react';
import { AlertCircle, AlertTriangle, ShieldAlert, RefreshCw, Info } from 'lucide-react';

export default function StatusCards({ response, onRetry }) {
  if (!response) return null;

  // 1. NO CONTEXT STATE
  if (response.grounding_status === 'NO_CONTEXT') {
    return (
      <div className="w-full mb-4 clean-card p-4 border border-sky-500/30 bg-sky-950/20 text-sky-200 animate-fadeIn">
        <div className="flex items-center gap-2 mb-1 font-mono font-bold text-xs text-sky-400">
          <Info className="w-4 h-4 shrink-0" />
          <span>⚠ Insufficient Context</span>
        </div>
        <p className="text-xs leading-relaxed text-slate-300">
          I couldn't find enough information in the knowledge base to answer this question. Try asking something related to available content.
        </p>
      </div>
    );
  }

  // 2. UNSAFE QUERY BLOCKED STATE
  if (response.grounding_status === 'UNSAFE_QUERY' || response.grounding_status === 'UNSAFE' || response.errorType === 'UNSAFE') {
    return (
      <div className="w-full mb-4 clean-card p-4 border border-amber-500/30 bg-amber-950/20 text-amber-200 animate-fadeIn">
        <div className="flex items-center gap-2 mb-1 font-mono font-bold text-xs text-amber-400">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>⚠ Request Blocked</span>
        </div>
        <p className="text-xs leading-relaxed text-slate-300">
          This request does not meet the system's safety requirements.
        </p>
      </div>
    );
  }

  // 3. RATE LIMITED (HTTP 429)
  if (response.errorType === 'RATE_LIMITED' || response.grounding_status === 'PROVIDER_TIMEOUT') {
    return (
      <div className="w-full mb-4 clean-card p-4 border border-rose-500/30 bg-rose-950/20 text-rose-200 animate-fadeIn">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2 font-mono font-bold text-xs text-rose-400">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>⚠ AI Service Temporarily Busy</span>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-2.5 py-0.5 rounded bg-rose-500/20 hover:bg-rose-500/30 text-[11px] font-mono text-rose-200 flex items-center gap-1 transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Retry</span>
            </button>
          )}
        </div>
        <p className="text-xs text-slate-300">
          Please try again shortly.
        </p>
      </div>
    );
  }

  // 4. PROVIDER ERROR / QUOTA
  if (response.errorType === 'PROVIDER_ERROR' || response.errorType === 'QUOTA_EXHAUSTED' || response.errorType === 'NETWORK_ERROR') {
    return (
      <div className="w-full mb-4 clean-card p-4 border border-rose-500/30 bg-rose-950/20 text-rose-200 animate-fadeIn">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2 font-mono font-bold text-xs text-rose-400">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>⚠ AI Service Unavailable</span>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-2.5 py-0.5 rounded bg-rose-500/20 hover:bg-rose-500/30 text-[11px] font-mono text-rose-200 flex items-center gap-1 transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Retry</span>
            </button>
          )}
        </div>
        <p className="text-xs text-slate-300">
          {response.message || 'Please try again later.'}
        </p>
      </div>
    );
  }

  return null;
}
