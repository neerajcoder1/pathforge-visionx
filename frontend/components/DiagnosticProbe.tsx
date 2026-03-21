'use client';
// components/DiagnosticProbe.tsx

import React, { useState } from 'react';
import { PaceResult } from '../types';
import { submitQuizResult } from '../lib/api';

interface DiagnosticProbeProps {
  sessionId: string;
  onResult: (result: PaceResult) => void;
  onClose: () => void;
}

const QUESTIONS = [
  {
    id: 0,
    text: 'Can you explain the difference between a SQL JOIN and a UNION?',
    topic: 'SQL & Databases',
  },
  {
    id: 1,
    text: 'What is the purpose of Docker container orchestration?',
    topic: 'DevOps',
  },
  {
    id: 2,
    text: 'Describe what overfitting means in machine learning.',
    topic: 'Machine Learning',
  },
  {
    id: 3,
    text: 'What is a REST API and what are the main HTTP methods?',
    topic: 'Web APIs',
  },
  {
    id: 4,
    text: 'Explain the difference between synchronous and asynchronous code.',
    topic: 'Programming',
  },
  {
    id: 5,
    text: 'What does CAP theorem mean for distributed systems?',
    topic: 'System Design',
  },
  {
    id: 6,
    text: 'What is gradient descent in the context of model training?',
    topic: 'Machine Learning',
  },
  {
    id: 7,
    text: 'Explain what a Kubernetes pod is and how it differs from a container.',
    topic: 'DevOps',
  },
  {
    id: 8,
    text: 'What is the difference between authentication and authorization?',
    topic: 'Security',
  },
  {
    id: 9,
    text: 'Describe what a message queue is and give a use case.',
    topic: 'System Design',
  },
];

export default function DiagnosticProbe({
  sessionId,
  onResult,
  onClose,
}: DiagnosticProbeProps) {
  const [answers, setAnswers] = useState<Record<number, boolean | null>>(
    Object.fromEntries(QUESTIONS.map((q) => [q.id, null]))
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const allAnswered = Object.values(answers).every((a) => a !== null);
  const answeredCount = Object.values(answers).filter((a) => a !== null).length;

  const handleToggle = (id: number, val: boolean) => {
    setAnswers((prev) => ({ ...prev, [id]: val }));
  };

  const handleSubmit = async () => {
    if (!allAnswered) return;
    setSubmitting(true);
    setError(null);

    try {
      const boolAnswers = QUESTIONS.map((q) => answers[q.id] === true);
      const result = await submitQuizResult({
        session_id: sessionId,
        module_id: 'diagnostic',
        answers: boolAnswers,
      });
      onResult(result);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-800 flex items-start justify-between shrink-0">
          <div>
            <h2 className="text-xl font-bold text-white">Diagnostic Assessment</h2>
            <p className="text-sm text-gray-400 mt-1">
              Answer honestly — this calibrates your personalized path.
              ({answeredCount}/{QUESTIONS.length} answered)
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-white text-xl leading-none mt-1 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Progress bar */}
        <div className="px-6 pt-3 shrink-0">
          <div className="w-full bg-gray-800 rounded-full h-1.5">
            <div
              className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${(answeredCount / QUESTIONS.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Questions */}
        <div className="overflow-y-auto flex-1 px-6 py-4 space-y-4">
          {QUESTIONS.map((q) => (
            <div
              key={q.id}
              className={`bg-gray-800 rounded-xl p-4 border transition-all duration-200 ${
                answers[q.id] !== null
                  ? 'border-blue-700'
                  : 'border-gray-700'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <span className="text-xs font-medium text-blue-400 bg-blue-900/30 px-2 py-0.5 rounded mb-2 inline-block">
                    {q.topic}
                  </span>
                  <p className="text-sm text-gray-200 mt-1">{q.text}</p>
                </div>
              </div>

              <div className="flex gap-3 mt-3">
                <button
                  onClick={() => handleToggle(q.id, true)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium border transition-all duration-150 ${
                    answers[q.id] === true
                      ? 'bg-green-600 border-green-500 text-white'
                      : 'bg-gray-700 border-gray-600 text-gray-300 hover:border-green-600 hover:text-green-400'
                  }`}
                >
                  ✓ Yes, I know this
                </button>
                <button
                  onClick={() => handleToggle(q.id, false)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium border transition-all duration-150 ${
                    answers[q.id] === false
                      ? 'bg-red-700 border-red-600 text-white'
                      : 'bg-gray-700 border-gray-600 text-gray-300 hover:border-red-600 hover:text-red-400'
                  }`}
                >
                  ✗ Not confident
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-800 shrink-0">
          {error && (
            <p className="text-red-400 text-sm mb-3">⚠️ {error}</p>
          )}
          <button
            onClick={handleSubmit}
            disabled={!allAnswered || submitting}
            className={`w-full py-3 rounded-xl font-bold text-sm transition-all duration-200 ${
              allAnswered && !submitting
                ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/30'
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            }`}
          >
            {submitting
              ? '⏳ Recalculating path...'
              : !allAnswered
              ? `Answer all questions (${answeredCount}/${QUESTIONS.length})`
              : '🚀 Submit & Recalculate Learning Path'}
          </button>
        </div>
      </div>
    </div>
  );
}
