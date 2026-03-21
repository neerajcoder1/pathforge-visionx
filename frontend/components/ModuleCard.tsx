'use client';
// components/ModuleCard.tsx

import React, { useState } from 'react';
import { CourseModule } from '../types';

interface ModuleCardProps {
  module: CourseModule;
  index: number;
}

export default function ModuleCard({ module, index }: ModuleCardProps) {
  const [showTrace, setShowTrace] = useState(false);
  const [hrMode, setHrMode] = useState(false);

  const z3Color = module.z3_result === 'PASS' ? 'text-green-300' : 'text-red-300';
  const z3Bg = module.z3_result === 'PASS' ? 'bg-green-900/40 border-green-700' : 'bg-red-900/40 border-red-700';

  const ciColor = (module as any).ci_color as 'green' | 'amber' | 'red' | undefined;
  const ciBorder = ciColor === 'green'
    ? 'border-green-600'
    : ciColor === 'red'
    ? 'border-red-600'
    : 'border-amber-500';

  const rawBefore = Number((module as any).bkt_before);
  const rawAfter = Number((module as any).bkt_after);
  const fallbackAfter = Math.min(1, Math.max(0, Number(module.bkt_delta || 0) + 0.35));
  const masteryAfter = Number.isFinite(rawAfter) ? rawAfter : fallbackAfter;
  const masteryBefore = Number.isFinite(rawBefore)
    ? rawBefore
    : Math.max(0, masteryAfter - Number(module.bkt_delta || 0));

  return (
    <div className={`bg-gray-800 rounded-xl border ${ciBorder} overflow-hidden hover:border-blue-600 transition-all duration-200`}>
      {/* Card Header */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <span className="shrink-0 w-7 h-7 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center mt-0.5">
              {index + 1}
            </span>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="font-semibold text-white text-sm">{module.title}</h3>
                {module.is_mandatory && (
                  <span className="shrink-0 text-xs bg-red-600 text-white px-2 py-0.5 rounded font-bold">
                    REQUIRED
                  </span>
                )}
                <span className="shrink-0 text-xs bg-gray-700 border border-gray-600 text-gray-200 px-2 py-0.5 rounded">
                  {module.hours}h
                </span>
              </div>
              <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                <span>
                  Mastery: {masteryBefore.toFixed(2)} -&gt; {masteryAfter.toFixed(2)}
                </span>
                <span>⭐ {(module.reward_score * 100).toFixed(0)}/100</span>
              </div>
            </div>
          </div>

          {/* Z3 Badge */}
          <span className={`shrink-0 text-xs font-mono font-bold px-2 py-1 rounded border ${z3Bg} ${z3Color}`}>
            {module.z3_result === 'PASS' ? 'Z3 VERIFIED' : 'Z3 FAILED'}
          </span>
        </div>

        {/* Why this? */}
        <div className="mt-3 text-xs text-gray-400 leading-relaxed pl-10">
          {module.justification_en}
        </div>

        {/* Action buttons */}
        <div className="mt-3 flex items-center gap-2 pl-10">
          <button
            onClick={() => setShowTrace(!showTrace)}
            className="text-xs text-blue-400 hover:text-blue-300 underline underline-offset-2 transition-colors"
          >
            {showTrace ? 'Hide' : 'Show'} technical trace
          </button>
          <span className="text-gray-600">·</span>
          <button
            onClick={() => setHrMode(!hrMode)}
            className="text-xs text-purple-400 hover:text-purple-300 underline underline-offset-2 transition-colors"
          >
            {hrMode ? 'Show JSON' : 'Plain English Summary'}
          </button>
        </div>
      </div>

      {/* Expandable Technical Trace */}
      {showTrace && (
        <div className="border-t border-gray-700 bg-gray-900 p-4">
          {hrMode ? (
            <div className="text-sm text-gray-300 leading-relaxed">
              <p className="font-semibold text-white mb-2">📋 HR Summary</p>
              <p>
                This course is recommended because the employee's current proficiency in this
                area is below the role requirement. Completing this {module.hours}-hour module
                is expected to increase their readiness score by approximately{' '}
                {Math.round(module.bkt_delta * 100)} percentage points.
              </p>
              {module.is_mandatory && (
                <p className="mt-2 text-red-400 font-medium">
                  ⚠️ This course is mandatory and cannot be skipped, regardless of prior
                  experience. It is required for compliance purposes.
                </p>
              )}
            </div>
          ) : (
            <div>
              <p className="text-xs font-semibold text-gray-400 mb-2">Technical Provenance</p>
              <pre className="text-xs text-green-300 bg-black rounded-lg p-3 overflow-x-auto leading-relaxed">
{JSON.stringify(
  {
    course_id: module.course_id,
    z3_result: module.z3_result,
    bkt_delta: module.bkt_delta,
    reward_score: module.reward_score,
    teaches: module.teaches,
    is_mandatory: module.is_mandatory,
    rejection_reason: module.rejection_reason ?? null,
  },
  null,
  2
)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
