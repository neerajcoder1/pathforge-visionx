'use client';
// pages/index.tsx

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { PaceResult } from '../types';
import { uploadResume, getDemoProfile } from '../lib/api';
import { useSSEStream, SSEStage } from '../hooks/useSSEStream';
import { MOCK_PACE_RESULT } from '../lib/mockData';

import SkillRadar from '../components/SkillRadar';
import ParetoPaths from '../components/ParetoPaths';
import TraceViewer from '../components/TraceViewer';
import HRDashboard from '../components/HRDashboard';
import DiagnosticProbe from '../components/DiagnosticProbe';

type ViewTab = 'radar' | 'paths' | 'trace' | 'hr';

const VIEW_TABS: { id: ViewTab; label: string; icon: string }[] = [
  { id: 'radar', label: 'Skill Radar', icon: '🎯' },
  { id: 'paths', label: 'Learning Paths', icon: '🗺️' },
  { id: 'trace', label: 'Trace Viewer', icon: '🔍' },
  { id: 'hr', label: 'HR Dashboard', icon: '📊' },
];

const STAGE_STEPS: SSEStage[] = ['extracting', 'computing', 'generating', 'verifying'];

export default function Home() {
  const [paceResult, setPaceResult] = useState<PaceResult | null>(null);
  const [activeView, setActiveView] = useState<ViewTab>('radar');
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [jdText, setJdText] = useState('');
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const [showDiagnostic, setShowDiagnostic] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { stage, stageLabel, isStreaming, startStream } = useSSEStream();

  // Clear potentially stale JD/session state on initial mount.
  useEffect(() => {
    setUploadedFile(null);
    setPaceResult(null);
    setUploadError(null);
    setJdText('');
    setSessionId(null);
  }, []);

  // ── File handling ──────────────────────────────────────────────────────────
  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith('.pdf')) {
      setUploadError('Please upload a PDF file.');
      return;
    }

    // Reset file/session/result only. Keep JD text intact for dynamic analyze flow.
    setSessionId(null);
    setPaceResult(null);
    setShowDiagnostic(false);
    setUploadError(null);
    setUploadedFile(file);
    setIsUploading(true);

    try {
      const res = await uploadResume(file);
      setSessionId(res.session_id);
    } catch {
      setSessionId(null);
      setUploadedFile(null);
      setUploadError('Upload failed. Please check backend connectivity and try again.');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  // ── Generate path ──────────────────────────────────────────────────────────
  const handleGenerate = useCallback(async () => {
    if (!sessionId || !jdText.trim()) return;

    try {
      const result = await startStream(sessionId, jdText);
      if (result?.session_id) {
        setPaceResult(result);
        setActiveView('radar');
      } else {
        setUploadError('Analysis failed. Please retry with a valid resume and JD.');
      }
    } catch {
      setUploadError('Analysis request failed. Please check backend connectivity.');
    }
  }, [sessionId, jdText, startStream]);

  // ── Load demo profile ──────────────────────────────────────────────────────
  const handleLoadDemo = useCallback(async (profileId: number = 1) => {
    setIsDemoLoading(true);
    setUploadError(null);
    try {
      const result = await getDemoProfile(profileId);
      setPaceResult(result);
    } catch {
      // Backend offline — use local mock
      setPaceResult(MOCK_PACE_RESULT);
    } finally {
      setIsDemoLoading(false);
      setActiveView('radar');
    }
  }, []);

  // ── Progress indicator stages ──────────────────────────────────────────────
  const currentStepIdx = STAGE_STEPS.indexOf(stage as SSEStage);

  // Use streamed result or explicitly set result
  const displayResult = paceResult;
  const safeCurrentMastery = displayResult?.current_mastery || [];
  const safeTargetSkills = displayResult?.target_skills || [];
  const safePathVariants = displayResult?.path_variants || [];

  const canGenerate =
    sessionId && jdText.trim().length > 20 && !isStreaming && !isUploading;

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Top Nav */}
      <nav className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-sm">N</div>
            <div>
              <span className="font-bold text-white text-sm">NEXUS</span>
              <span className="text-gray-500 text-xs ml-2">AI-Adaptive Onboarding Engine</span>
            </div>
          </div>
          <div className="text-xs text-gray-500">HR Judge Mode</div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {!displayResult ? (
          /* ─── UPLOAD / INPUT AREA ─── */
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-extrabold text-white mb-2">
                Personalized <span className="text-blue-400">Learning Paths</span>
              </h1>
              <p className="text-gray-400 text-base">
                Upload a resume + paste a job description → get a Z3-verified,
                BKT-calibrated onboarding plan in seconds.
              </p>
            </div>

            {/* PDF Drop Zone */}
            <div
              onDrop={handleDrop}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 ${
                isDragging
                  ? 'border-blue-500 bg-blue-900/20'
                  : uploadedFile
                  ? 'border-green-600 bg-green-900/10'
                  : 'border-gray-700 hover:border-gray-600 bg-gray-900'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={handleFileInput}
              />
              {isUploading ? (
                <div className="text-blue-400 animate-pulse text-sm">⏳ Uploading...</div>
              ) : uploadedFile ? (
                <div>
                  <div className="text-green-400 text-3xl mb-2">✓</div>
                  <div className="text-green-400 font-medium text-sm">{uploadedFile.name}</div>
                  {sessionId && (
                    <div className="text-xs text-gray-500 mt-1 font-mono">
                      session: {sessionId}
                    </div>
                  )}
                  <div className="text-xs text-gray-500 mt-2">Click to change file</div>
                </div>
              ) : (
                <div>
                  <div className="text-4xl mb-3">📄</div>
                  <div className="text-gray-300 font-medium text-sm">
                    Drag & drop your resume PDF
                  </div>
                  <div className="text-gray-600 text-xs mt-1">or click to browse</div>
                </div>
              )}
            </div>

            {uploadError && (
              <p className="text-red-400 text-sm text-center">{uploadError}</p>
            )}

            {/* JD Text Area */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Job Description
              </label>
              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the job description here..."
                rows={6}
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-600 resize-none transition-colors"
              />
              <p className="text-xs text-gray-600 mt-1">{jdText.length} characters</p>
            </div>

            {/* SSE Progress */}
            {isStreaming && (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm text-blue-400 font-medium">{stageLabel}</span>
                </div>
                <div className="flex gap-2">
                  {STAGE_STEPS.map((s, i) => (
                    <div
                      key={s}
                      className={`flex-1 h-1.5 rounded-full transition-all duration-500 ${
                        i <= currentStepIdx ? 'bg-blue-500' : 'bg-gray-700'
                      }`}
                    />
                  ))}
                </div>
                <div className="flex justify-between text-[10px] text-gray-600 mt-1">
                  <span>Extracting</span>
                  <span>Mastery</span>
                  <span>Paths</span>
                  <span>Z3 Verify</span>
                </div>
              </div>
            )}

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={!canGenerate}
              className={`w-full py-4 rounded-xl font-bold text-base transition-all duration-200 ${
                canGenerate
                  ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/40 hover:shadow-blue-900/60'
                  : 'bg-gray-800 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isStreaming ? '⏳ Generating...' : '🚀 Generate Learning Path'}
            </button>

            <button
              onClick={() => handleLoadDemo(1)}
              disabled={isDemoLoading || isStreaming}
              className="w-full py-3 rounded-xl font-semibold text-sm border border-gray-600 bg-gray-800/70 text-gray-200 hover:bg-gray-700 hover:border-gray-500 transition-colors disabled:opacity-50"
            >
              {isDemoLoading
                ? '⏳ Loading Demo...'
                : '✨ Load Pre-Configured Demo (SWE → Logistics)'}
            </button>
          </div>
        ) : (
          /* ─── RESULTS AREA ─── */
          <div className="space-y-6">
            {/* Result header */}
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div>
                <h1 className="text-2xl font-bold text-white">Learning Path Generated</h1>
                <p className="text-gray-400 text-sm mt-0.5 font-mono">
                  session: {displayResult?.session_id || 'unknown-session'}
                </p>
              </div>
              <div className="flex items-center gap-3">
                {displayResult?.diagnostic_required && (
                  <button
                    onClick={() => setShowDiagnostic(true)}
                    className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium transition-colors shadow-lg"
                  >
                    🔬 Diagnostic Probe
                  </button>
                )}
                <button
                  onClick={() => {
                    setPaceResult(null);
                    setUploadedFile(null);
                    setSessionId(null);
                    setJdText('');
                  }}
                  className="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm border border-gray-700 transition-colors"
                >
                  ↩ Start Over
                </button>
              </div>
            </div>

            {/* View Tabs */}
            <div className="flex gap-1 bg-gray-900 rounded-xl p-1 border border-gray-800 w-fit">
              {VIEW_TABS.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveView(tab.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2 ${
                    activeView === tab.id
                      ? 'bg-blue-600 text-white shadow'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Active View */}
            {activeView === 'radar' && (
              <SkillRadar
                currentMastery={safeCurrentMastery}
                targetSkills={safeTargetSkills}
              />
            )}
            {activeView === 'paths' && (
              <ParetoPaths
                pathVariants={safePathVariants}
                cvsNexus={displayResult?.cvs_nexus}
                cvsLegacy={displayResult?.cvs_legacy}
              />
            )}
            {activeView === 'trace' && (
              displayResult ? <TraceViewer result={displayResult} /> : <div className="text-white">Loading or Invalid Data...</div>
            )}
            {activeView === 'hr' && (
              displayResult ? <HRDashboard result={displayResult} /> : <div className="text-white">Loading or Invalid Data...</div>
            )}
          </div>
        )}
      </div>

      {/* Diagnostic Probe Modal */}
      {showDiagnostic && displayResult && (
        <DiagnosticProbe
          sessionId={displayResult.session_id}
          onResult={(updated) => {
            setPaceResult(updated);
            setShowDiagnostic(false);
          }}
          onClose={() => setShowDiagnostic(false)}
        />
      )}
    </div>
  );
}
