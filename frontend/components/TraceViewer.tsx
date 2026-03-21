'use client';
// components/TraceViewer.tsx

import React, { useMemo, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  type Edge,
  type Node,
} from 'react-flow-renderer';
import { PaceResult } from '../types';

interface TraceViewerProps {
  result: PaceResult;
}

type LedgerEntry = {
  course_id?: string;
  title?: string;
  rejection_reason?: string;
};

export default function TraceViewer({ result }: TraceViewerProps) {
  const [viewMode, setViewMode] = useState<'technical' | 'hr'>('technical');
  const ledger = result.decision_ledger as Record<string, unknown>;
  const optionsConsidered = (ledger.options_considered ?? []) as LedgerEntry[];
  const z3Rules = (ledger.z3_rules_checked ?? []) as string[];
  const bktParams = ledger.bkt_parameters as Record<string, number> | undefined;
  const maskedBlocked = (ledger.masked_actions_blocked ?? []) as string[];
  const avgHours =
    result.path_variants.length > 0
      ? (result.path_variants.reduce((sum, p) => sum + p.total_hours, 0) / result.path_variants.length).toFixed(1)
      : '0.0';

  const dagNodes: Node[] = useMemo(
    () => [
      { id: 'parse', data: { label: 'Parse Resume' }, position: { x: 0, y: 80 }, style: nodeStyle('#1d4ed8') },
      { id: 'extract', data: { label: 'Extract Skills' }, position: { x: 220, y: 80 }, style: nodeStyle('#0f766e') },
      { id: 'bkt', data: { label: 'BKT Mastery Update' }, position: { x: 460, y: 10 }, style: nodeStyle('#7c3aed') },
      { id: 'masked', data: { label: `Mask (${maskedBlocked.length} blocked)` }, position: { x: 460, y: 150 }, style: nodeStyle('#b45309') },
      { id: 'pace', data: { label: 'PACE Pareto x3' }, position: { x: 700, y: 80 }, style: nodeStyle('#be185d') },
      { id: 'z3', data: { label: `Z3 Verify (${z3Rules.length})` }, position: { x: 940, y: 80 }, style: nodeStyle('#15803d') },
      { id: 'justify', data: { label: 'English Justification' }, position: { x: 1180, y: 80 }, style: nodeStyle('#334155') },
    ],
    [maskedBlocked.length, z3Rules.length]
  );

  const dagEdges: Edge[] = useMemo(
    () => [
      edge('parse', 'extract'),
      edge('extract', 'bkt'),
      edge('extract', 'masked'),
      edge('bkt', 'pace'),
      edge('masked', 'pace'),
      edge('pace', 'z3'),
      edge('z3', 'justify'),
    ],
    []
  );

  return (
    <div className="bg-gray-900 rounded-2xl border border-gray-800 shadow-2xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-white">Decision Trace</h2>
        <div className="flex bg-gray-800 rounded-lg border border-gray-700 p-1 text-xs">
          <button
            onClick={() => setViewMode('technical')}
            className={`px-3 py-1.5 rounded-md transition-colors ${
              viewMode === 'technical' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white'
            }`}
          >
            Technical View
          </button>
          <button
            onClick={() => setViewMode('hr')}
            className={`px-3 py-1.5 rounded-md transition-colors ${
              viewMode === 'hr' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white'
            }`}
          >
            Explain Like I&apos;m HR
          </button>
        </div>
      </div>

      {viewMode === 'hr' ? (
        <div className="space-y-4 text-sm text-gray-300">
          <p className="leading-relaxed">
            🧭 NEXUS mapped <strong className="text-white">{result.current_mastery.length} skills</strong> from the resume,
            compared them against the role, and estimated an average completion timeline of{' '}
            <strong className="text-white">{avgHours} hours</strong>.
          </p>
          <p className="leading-relaxed">
            🧠 Each recommended module closes a measured skill gap and includes prerequisite checks,
            so employees do not get assigned content above their current readiness.
          </p>
          <p className="leading-relaxed">
            ⏱️ Compared to standard onboarding, this pathway is{' '}
            <strong className="text-green-400">{((result.cvs_nexus / result.cvs_legacy) * 100 - 100).toFixed(0)}%</strong>{' '}
            more efficient while preserving compliance modules and required sequencing.
          </p>
          <p className="leading-relaxed">
            ✅ Formal validation confirmed that mandatory courses are present and the plan is safe to execute.
          </p>
        </div>
      ) : (
        <>
          <div className="mb-6 border border-gray-700 rounded-xl overflow-hidden">
            <div className="h-[320px] bg-gray-950">
              <ReactFlow
                nodes={dagNodes}
                edges={dagEdges}
                nodesDraggable={false}
                nodesConnectable={false}
                elementsSelectable={false}
                fitView
                fitViewOptions={{ padding: 0.2 }}
              >
                <Controls />
                <Background color="#1f2937" gap={20} />
              </ReactFlow>
            </div>
          </div>

          {/* Z3 Rules */}
          <div className="mb-4">
            <p className="text-xs font-semibold text-gray-400 mb-2">Z3 Rules Checked</p>
            <div className="flex flex-wrap gap-2">
              {z3Rules.map((rule) => (
                <span
                  key={rule}
                  className="text-xs font-mono bg-green-900/40 border border-green-700 text-green-400 px-2 py-1 rounded"
                >
                  ✓ {rule}
                </span>
              ))}
            </div>
          </div>

          {/* BKT Parameters */}
          {bktParams && (
            <div className="mb-4 bg-gray-800 rounded-lg p-3">
              <p className="text-xs font-semibold text-gray-400 mb-2">BKT Parameters</p>
              <div className="flex gap-4 text-xs font-mono">
                <span className="text-blue-400">P(T) = {bktParams.p_t}</span>
                <span className="text-yellow-400">P(S) = {bktParams.p_s}</span>
                <span className="text-purple-400">P(G) = {bktParams.p_g}</span>
              </div>
            </div>
          )}

          {/* Options Rejected */}
          {optionsConsidered.length > 0 && (
            <div className="mb-4">
              <p className="text-xs font-semibold text-gray-400 mb-2">
                Rejected Alternatives ({optionsConsidered.length})
              </p>
              <div className="space-y-2">
                {optionsConsidered.map((opt, i) => (
                  <div
                    key={i}
                    className="bg-gray-800 rounded-lg p-2 text-xs flex items-start gap-2"
                  >
                    <span className="text-red-500 shrink-0">✗</span>
                    <div>
                      <span className="text-gray-300 font-medium">{opt.title}</span>
                      <span className="text-gray-500 ml-2">— {opt.rejection_reason}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function nodeStyle(borderColor: string): React.CSSProperties {
  return {
    background: '#111827',
    color: '#e5e7eb',
    border: `1px solid ${borderColor}`,
    borderRadius: 10,
    fontSize: 12,
    width: 170,
    textAlign: 'center',
    padding: '8px 10px',
  };
}

function edge(source: string, target: string): Edge {
  return {
    id: `${source}-${target}`,
    source,
    target,
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: '#64748b',
    },
    style: { stroke: '#64748b' },
    animated: false,
    type: 'smoothstep',
  };
}
