/**
 * API Client for RAGE HH GOA Backend
 * Endpoints: GET /health, POST /ask, POST /transcribe
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function checkBackendHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);
    
    const res = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    
    if (!res.ok) return { online: false };
    const data = await res.json();
    return { online: data.status === 'ok' || data.status === 'healthy', data };
  } catch (err) {
    return { online: false, error: err.message };
  }
}

export async function sendAskQuestion({ query, top_k = 3, language_filter = null, preferred_answer_language = null }) {
  const payload = {
    query,
    top_k: Number(top_k),
    language_filter: language_filter && language_filter !== 'auto' ? language_filter : null,
    preferred_answer_language: preferred_answer_language && preferred_answer_language !== 'auto' ? preferred_answer_language : null
  };

  try {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (response.status === 429) {
      return {
        errorType: 'RATE_LIMITED',
        statusCode: 429,
        message: 'The AI service is currently handling too many requests. Please try again shortly.'
      };
    }

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      const detailStr = String(errData.detail || '');
      
      if (detailStr.toLowerCase().includes('quota') || detailStr.toLowerCase().includes('limit')) {
        return {
          errorType: 'QUOTA_EXHAUSTED',
          statusCode: response.status,
          message: 'The AI service has reached its current usage limit. Please try again later.'
        };
      }

      return {
        errorType: 'PROVIDER_ERROR',
        statusCode: response.status,
        message: 'The AI service is temporarily unavailable. Please try again later.'
      };
    }

    const data = await response.json();
    return data;
  } catch (err) {
    return {
      errorType: 'NETWORK_ERROR',
      statusCode: 0,
      message: 'Unable to connect to the backend service. Please verify server connection.'
    };
  }
}

export async function transcribeAudio({ audioBlob, language = 'en' }) {
  const formData = new FormData();
  formData.append('file', audioBlob, 'recording.webm');
  formData.append('language', language || 'en');

  const startTime = performance.now();
  try {
    const response = await fetch(`${API_BASE_URL}/transcribe`, {
      method: 'POST',
      body: formData,
    });

    const elapsed = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      return {
        success: false,
        stt_latency_ms: elapsed,
        error_message: errData.detail || `Speech-to-Text error (${response.status})`
      };
    }

    const data = await response.json();
    if (!data.stt_latency_ms) {
      data.stt_latency_ms = elapsed;
    }
    return data;
  } catch (err) {
    const elapsed = Math.round(performance.now() - startTime);
    return {
      success: false,
      stt_latency_ms: elapsed,
      error_message: err.message || 'Speech-to-Text network error'
    };
  }
}
