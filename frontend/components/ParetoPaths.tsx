'use client';
// components/ParetoPaths.tsx

import React, { useState } from 'react';
import { PathVariant } from '../types';
import ModuleCard from './ModuleCard';

interface ParetoPathsProps {
  pathVariants: PathVariant[];
  cvsNexus?: number;
  cvsLegacy?: number;
}

const TAB_META: Record<string, { icon: string; color: string; desc: string; lambda: string }> = {
  Speed: {
    icon: '⚡',
    color: 'text-yellow-400 border-yellow-500 bg-yellow-900/20',
    desc: 'Fastest path to minimum viable mastery. Prioritizes critical gaps only.',
    lambda: '2.0',
  },
  Balance: {
    icon: '⚖️',
    color: 'text-blue-400 border-blue-500 bg-blue-900/20',
    desc: 'Optimal balance of time investment and skill coverage.',
    lambda: '1.0',
  },
  Depth: {
    icon: '🎯',
    color: 'text-purple-400 border-purple-500 bg-purple-900/20',
    desc: 'Maximum mastery depth. Every skill taken to senior-level proficiency.',
    lambda: '0.2',
  },
};

const TAB_ORDER: Array<'Speed' | 'Balance' | 'Depth'> = ['Speed', 'Balance', 'Depth'];

export default function ParetoPaths({ pathVariants, cvsNexus, cvsLegacy }: ParetoPathsProps) {
  const safePathVariants = (Array.isArray(pathVariants) ? pathVariants : []) || [];
  if (!safePathVariants.length) {
    return <div className="text-white">Loading or Invalid Data...</div>;
  }

  const variantByLabel: Record<string, PathVariant | undefined> = {
    Speed: safePathVariants.find((p) => p.label === 'Speed') ?? safePathVariants[0],
    Balance: safePathVariants.find((p) => p.label === 'Balance') ?? safePathVariants[0],
    Depth: safePathVariants.find((p) => p.label === 'Depth') ?? safePathVariants[0],
  };

  const [activeTab, setActiveTab] = useState<'Speed' | 'Balance' | 'Depth'>('Speed');

  const activePath = variantByLabel[activeTab];

  if (!activePath) return <div className="text-white">Loading or Invalid Data...</div>;

  const standardHours =
    cvsLegacy && cvsNexus && cvsLegacy > 0
      ? Math.round(activePath.total_hours * (cvsNexus / cvsLegacy))
      : Math.round(activePath.total_hours * 2.5);
  const hoursSaved = Math.max(0, standardHours - activePath.total_hours);

  return (
    <div className="bg-gray-900 rounded-2xl border border-gray-800 shadow-2xl overflow-hidden">
      {/* Tab Bar */}
      <div className="flex border-b border-gray-800">
        {TAB_ORDER.map((tabLabel) => {
          const variant = variantByLabel[tabLabel];
          if (!variant) return null;
          const meta = TAB_META[tabLabel] ?? {
            icon: '📋',
            color: 'text-gray-400 border-gray-600 bg-gray-800',
            desc: '',
            lambda: '-',
          };
          const isActive = activeTab === tabLabel;
          return (
            <button
              key={tabLabel}
              onClick={() => setActiveTab(tabLabel)}
              className={`flex-1 px-4 py-3 text-sm font-semibold transition-all duration-200 border-b-2 ${
                isActive
                  ? `${meta.color}`
                  : 'text-gray-500 border-transparent hover:text-gray-300'
              }`}
            >
              <div className="flex flex-col items-start">
                <span>
                  <span className="mr-1">{meta.icon}</span>
                  {tabLabel} (λ={meta.lambda})
                </span>
                <span className="text-[10px] font-normal text-gray-400 mt-1">
                  {variant.total_hours}h • {Number(variant.skill_coverage_pct ?? 0)}% • CVS {Number(variant.cvs ?? 0).toFixed(2)}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Tab Stats Row */}
      <div className="px-6 pt-4 pb-2">
        <p className="text-xs text-gray-500 mb-3">
          {TAB_META[activeTab]?.desc}
        </p>
        <div className="grid grid-cols-4 gap-3">
          <StatCard label="Total Hours" value={`${activePath.total_hours}h`} color="text-white" />
          <StatCard
            label="CVS"
            value={`${Number(activePath?.cvs ?? 0).toFixed(2)}x`}
            color="text-green-400"
            tooltip="Competency Velocity Score: mastery gain per training hour"
          />
          <StatCard
            label="Coverage"
            value={`${Number(activePath?.skill_coverage_pct ?? 0)}%`}
            color="text-blue-400"
          />
          <StatCard
            label="Z3 Verified"
            value={activePath?.z3_verified ? '✓ PASS' : '✗ FAIL'}
            color={activePath?.z3_verified ? 'text-green-400' : 'text-red-400'}
          />
        </div>
      </div>

      {/* λ tag */}
      <div className="px-6 pb-3">
        <span className="text-xs text-gray-500">
          Optimization objective λ={TAB_META[activeTab]?.lambda}: same planner, different trade-off surface.
        </span>
      </div>

      {/* Standard vs NEXUS comparison panel */}
      <div className="px-6 pb-4">
        <div className="rounded-xl border border-blue-800 bg-blue-900/10 p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <p className="text-[11px] text-gray-400 uppercase tracking-wide">Standard Path</p>
            <p className="text-2xl font-bold text-gray-200">{standardHours}h</p>
          </div>
          <div>
            <p className="text-[11px] text-gray-400 uppercase tracking-wide">NEXUS {activeTab}</p>
            <p className="text-2xl font-bold text-blue-300">{activePath.total_hours}h</p>
          </div>
          <div>
            <p className="text-[11px] text-gray-400 uppercase tracking-wide">Total Hours Saved</p>
            <p className="text-2xl font-bold text-emerald-400">{hoursSaved}h</p>
          </div>
        </div>
      </div>

      {/* Module List */}
      <div className="px-6 pb-6 space-y-3">
        {((activePath?.modules || []) as any[]).map((mod, i) => (
          <ModuleCard key={mod?.course_id || i} module={mod} index={i} />
        ))}
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  color,
  tooltip,
}: {
  label: string;
  value: string;
  color: string;
  tooltip?: string;
}) {
  return (
    <div
      className="bg-gray-800 rounded-lg p-3 text-center cursor-default"
      title={tooltip}
    >
      <div className={`text-lg font-bold font-mono ${color}`}>{value}</div>
      <div className="text-xs text-gray-500 mt-0.5">{label}</div>
    </div>
  );
}
