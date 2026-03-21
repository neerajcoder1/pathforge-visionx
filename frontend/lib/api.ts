// lib/api.ts — all backend calls go through here, NEVER raw fetch() in components

import {
  PaceResult,
  QuizResultRequest,
  SSEEvent,
  UploadResumeResponse,
} from '../types';

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ── Upload a PDF resume ──────────────────────────────────────────────────────
export async function uploadResume(
  file: File
): Promise<UploadResumeResponse> {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${BASE_URL}/api/upload-resume`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Upload failed: ${err}`);
  }

  return res.json() as Promise<UploadResumeResponse>;
}

// ── Analyze JD via SSE stream ────────────────────────────────────────────────
export async function analyzeJD(
  session_id: string,
  jd_text: string,
  onEvent: (event: SSEEvent) => void
): Promise<PaceResult> {
  const res = await fetch(`${BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, jd_text }),
  });

  if (!res.ok) {
    throw new Error(`Analyze failed: ${res.status}`);
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let finalResult: PaceResult | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n\n');
    buffer = lines.pop() ?? '';

    for (const chunk of lines) {
      const dataLine = chunk
        .split('\n')
        .find((l) => l.startsWith('data:'));
      if (!dataLine) continue;

      try {
        const raw = dataLine.slice(5).trim();
        const event: SSEEvent = JSON.parse(raw);
        onEvent(event);

        if (event.event_type === 'complete') {
          finalResult = event.payload as PaceResult;
        }
      } catch {
        // ignore malformed event
      }
    }
  }

  if (!finalResult) {
    throw new Error('SSE stream ended without complete event');
  }

  return finalResult;
}

// ── Submit diagnostic quiz result ────────────────────────────────────────────
export async function submitQuizResult(
  req: QuizResultRequest
): Promise<PaceResult> {
  const res = await fetch(`${BASE_URL}/api/quiz-result`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    throw new Error(`Quiz submit failed: ${res.status}`);
  }

  return res.json() as Promise<PaceResult>;
}

// ── Get pre-cached demo profile (instant, no LLM calls) ──────────────────────
export async function getDemoProfile(profileId: number): Promise<PaceResult> {
  const res = await fetch(`${BASE_URL}/api/demo/${profileId}`, {
    method: 'GET',
  });

  if (!res.ok) {
    throw new Error(`Demo profile ${profileId} failed: ${res.status}`);
  }

  return res.json() as Promise<PaceResult>;
}
