'use client';
// components/SkillRadar.tsx

import React, { useEffect, useMemo, useState } from 'react';
import { animate, useMotionValue } from 'framer-motion';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { SkillMastery } from '../types';

interface SkillRadarProps {
  currentMastery: SkillMastery[];
  targetSkills: SkillMastery[];
}

const CI_COLOR_MAP: Record<string, string> = {
  green: '#22c55e',
  amber: '#f59e0b',
  red: '#ef4444',
};

export default function SkillRadar({
  currentMastery,
  targetSkills,
}: SkillRadarProps) {
  const [progress, setProgress] = useState(0);
  const motionProgress = useMotionValue(0);

  if (!currentMastery || !targetSkills) {
    return <div className="text-white">Loading or Invalid Data...</div>;
  }

  const safeCurrent = (Array.isArray(currentMastery) ? currentMastery : []) || [];
  const safeTarget = (Array.isArray(targetSkills) ? targetSkills : []) || [];

  const data = useMemo(() => {
    const rankedData = (safeCurrent?.map((skill) => {
      const skillId = (skill as any)?.esco_uri ?? (skill as any)?.label ?? (skill as any)?.skill;
      const target = safeTarget.find(
        (t) =>
          (t as any)?.esco_uri === skillId ||
          (t as any)?.label === (skill as any)?.label ||
          (t as any)?.skill === (skill as any)?.skill
      );
      const pL0 = Number((skill as any)?.p_l0 ?? (skill as any)?.level ?? 0);
      const currentPm = Number((skill as any)?.p_m ?? (skill as any)?.level ?? 0);
      const targetPm = Number((target as any)?.p_m ?? (target as any)?.level ?? 1);
      const ciLower = Number((skill as any)?.ci_lower ?? 0);
      const ciUpper = Number((skill as any)?.ci_upper ?? 0);
      const ciColor = String((skill as any)?.ci_color ?? 'amber');
      const gap = Math.max(0, targetPm - currentPm, pL0 - currentPm);
      return {
        skill: (skill as any)?.label || (skill as any)?.skill || 'Unknown Skill',
        current: Math.round((Number.isFinite(currentPm) ? currentPm : 0) * 100),
        required: Math.round((Number.isFinite(targetPm) ? targetPm : 1) * 100),
        gap,
        ciColor,
        ci_lower: Math.round((Number.isFinite(ciLower) ? ciLower : 0) * 100),
        ci_upper: Math.round((Number.isFinite(ciUpper) ? ciUpper : 0) * 100),
        evidence: (skill as any)?.evidence || '',
      };
    }) || []).filter((row) => Number.isFinite(row?.current) && Number.isFinite(row?.required));

    return rankedData
      .sort((a, b) => {
        if (b.gap !== a.gap) return b.gap - a.gap;
        return b.ci_upper - a.ci_upper;
      })
      .slice(0, 12);
  }, [safeCurrent, safeTarget]);

  useEffect(() => {
    motionProgress.set(0);
    setProgress(0);
    const controls = animate(motionProgress, 1, {
      duration: 1.2,
      ease: 'easeOut',
      onUpdate: (latest) => setProgress(latest),
    });
    return () => controls.stop();
  }, [motionProgress, data.length]);

  const chartData = data.map((row) => ({
    ...row,
    currentAnimated: Math.round(row.current * progress),
  }));

  if (!data.length) {
    return (
      <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 shadow-2xl text-center">
        <h2 className="text-lg font-bold text-white">Skill Mastery Radar</h2>
        <p className="text-sm text-gray-400 mt-2">No skill data available for radar rendering.</p>
      </div>
    );
  }

  const CustomTooltip = ({
    active,
    payload,
    label,
  }: {
    active?: boolean;
    payload?: Array<{ color: string; name: string; value: number }>;
    label?: string;
  }) => {
    if (!active || !payload?.length) return null;
    const row = data.find((d) => d.skill === label);
    return (
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-xs max-w-xs shadow-xl">
        <p className="font-bold text-white mb-1">{label}</p>
        {payload.map((p) => (
          <p key={p.name} style={{ color: p.color }}>
            {p.name}: {p.value}%
          </p>
        ))}
        {row && (
          <>
            <p className="text-gray-400 mt-1">
              CI: [{row.ci_lower}%, {row.ci_upper}%]
            </p>
            <p className="text-gray-500 mt-1 italic truncate">{row.evidence}</p>
          </>
        )}
      </div>
    );
  };

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-white">Skill Mastery Radar</h2>
        <div className="flex gap-4 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-blue-500 inline-block" />
            <span className="text-gray-400">Current Mastery</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-orange-400 inline-block" />
            <span className="text-gray-400">Required by JD</span>
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={360}>
        <RadarChart data={chartData}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis
            dataKey="skill"
            tick={{ fill: '#9ca3af', fontSize: 11 }}
          />
          <Radar
            name="Current Mastery"
            dataKey="currentAnimated"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.35}
            isAnimationActive={false}
          />
          <Radar
            name="Required by JD"
            dataKey="required"
            stroke="#fb923c"
            fill="#fb923c"
            fillOpacity={0.15}
            strokeDasharray="5 5"
            isAnimationActive={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ color: '#9ca3af', fontSize: 12 }}
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* Top 3 skill gaps summary row */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-2">
        {data.slice(0, 3).map((row, idx) => {
          const ciColor = String(row.ciColor ?? 'amber');
          const skillKey = row.skill || idx;
          return (
          <div
            key={skillKey}
            className="flex items-center justify-between bg-gray-800 rounded-lg px-3 py-2 text-xs border"
            style={{ borderColor: CI_COLOR_MAP[ciColor] || CI_COLOR_MAP.amber }}
          >
            <span className="text-gray-300 truncate mr-2">{row.skill || 'Unknown Skill'}</span>
            <span
              className="font-mono font-bold shrink-0"
              style={{ color: CI_COLOR_MAP[ciColor] || CI_COLOR_MAP.amber }}
            >
              Gap: {Math.round(row.gap * 100)}%
            </span>
          </div>
        );})}
      </div>
    </div>
  );
}
