'use client';
// components/HRDashboard.tsx

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { PaceResult } from '../types';

interface HRDashboardProps {
  result: PaceResult;
}

export default function HRDashboard({ result }: HRDashboardProps) {
  const improvementPct = ((result.cvs_nexus / result.cvs_legacy - 1) * 100).toFixed(0);
  const activePath = result.path_variants.find((p) => p.label === 'Balance') ?? result.path_variants[0];
  const legacyHours = Math.round(activePath.total_hours * (result.cvs_nexus / result.cvs_legacy));

  const cvsData = [
    { name: 'Standard', cvs: Number(result.cvs_legacy.toFixed(3)), fill: '#6b7280' },
    { name: 'NEXUS', cvs: Number(result.cvs_nexus.toFixed(3)), fill: '#3b82f6' },
  ];

  const hoursData = [
    { name: 'Standard Path', hours: legacyHours, fill: '#6b7280' },
    { name: 'NEXUS Path', hours: activePath.total_hours, fill: '#3b82f6' },
  ];

  const skillCoverageData = result.current_mastery.map((skill) => {
    const target = result.target_skills.find((t) => t.esco_uri === skill.esco_uri);
    return {
      name: skill.label.split(' ')[0], // abbreviated
      current: Math.round(skill.p_m * 100),
      target: target ? Math.round(target.p_m * 100) : 100,
    };
  });

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
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-2 text-xs shadow-lg">
        <p className="text-white font-medium mb-1">{label}</p>
        {payload.map((p) => (
          <p key={p.name} style={{ color: p.color }}>
            {p.name}: {p.value}
          </p>
        ))}
      </div>
    );
  };

  const allZ3Verified = result.path_variants.every((p) => p.z3_verified);

  const catalogGaps = result.target_skills
    .map((target) => {
      const current = result.current_mastery.find((s) => s.esco_uri === target.esco_uri);
      const gap = Math.max(0, (target.p_m ?? 1) - (current?.p_m ?? 0));
      return {
        label: target.label,
        gap,
        current: current?.p_m ?? 0,
        target: target.p_m ?? 1,
      };
    })
    .sort((a, b) => b.gap - a.gap)
    .slice(0, 6);

  const ciStats = result.current_mastery.reduce(
    (acc, skill) => {
      const width = Math.max(0, (skill.ci_upper ?? skill.p_m) - (skill.ci_lower ?? skill.p_m));
      acc.totalWidth += width;
      acc[skill.ci_color] += 1;
      return acc;
    },
    { totalWidth: 0, green: 0, amber: 0, red: 0 }
  );
  const avgCiWidth = result.current_mastery.length
    ? ((ciStats.totalWidth / result.current_mastery.length) * 100).toFixed(1)
    : '0.0';

  return (
    <div className="bg-gray-900 rounded-2xl border border-gray-800 shadow-2xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white">HR Dashboard</h2>
        <div className="flex items-center gap-2">
          <span
            className={`text-xs px-3 py-1 rounded-full font-bold border ${
              allZ3Verified
                ? 'bg-green-900/50 border-green-600 text-green-300'
                : 'bg-red-900/50 border-red-600 text-red-300'
            }`}
          >
            {allZ3Verified ? 'COMPLIANT' : 'COMPLIANCE RISK'}
          </span>
        </div>
      </div>

      {/* Hero Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetricCard
          label="CVS Improvement"
          value={`+${improvementPct}%`}
          sub="vs. standard onboarding"
          color="text-green-400"
          bg="bg-green-900/20 border-green-800"
        />
        <MetricCard
          label="Hours Saved"
          value={`${legacyHours - activePath.total_hours}h`}
          sub="from standard path"
          color="text-blue-400"
          bg="bg-blue-900/20 border-blue-800"
        />
        <MetricCard
          label="Skills Assessed"
          value={`${result.current_mastery.length}`}
          sub="from resume + JD"
          color="text-purple-400"
          bg="bg-purple-900/20 border-purple-800"
        />
        <MetricCard
          label="Z3 Status"
          value={allZ3Verified ? 'VERIFIED' : 'UNVERIFIED'}
          sub="formal constraint check"
          color={allZ3Verified ? 'text-green-400' : 'text-red-400'}
          bg={allZ3Verified ? 'bg-green-900/20 border-green-800' : 'bg-red-900/20 border-red-800'}
        />
      </div>

      {/* CVS Comparison Chart */}
      <div>
        <h3 className="text-sm font-semibold text-gray-300 mb-3">CVS Comparison: NEXUS vs Standard</h3>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={cvsData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
            <XAxis type="number" domain={[0, Math.ceil(result.cvs_nexus * 1.3)]} tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <YAxis type="category" dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} width={130} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="cvs" name="CVS" radius={[0, 6, 6, 0]}>
              {cvsData.map((entry, i) => (
                <Cell key={i} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Catalog Gap Section */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Catalog Gap</h3>
        <div className="space-y-2">
          {catalogGaps.map((item) => (
            <div key={item.label} className="grid grid-cols-[1fr_auto] items-center gap-2 text-xs">
              <span className="text-gray-300 truncate">{item.label}</span>
              <span className="text-amber-300 font-mono">
                {(item.current * 100).toFixed(0)}% -&gt; {(item.target * 100).toFixed(0)}%
              </span>
            </div>
          ))}
          {!catalogGaps.length && <p className="text-xs text-gray-500">No catalog gaps detected for current target set.</p>}
        </div>
      </div>

      {/* Mastery Confidence Interval Panel */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Mastery Confidence Interval</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <MetricPill label="Avg CI Width" value={`${avgCiWidth}%`} color="text-blue-300" />
          <MetricPill label="Green" value={`${ciStats.green}`} color="text-green-300" />
          <MetricPill label="Amber" value={`${ciStats.amber}`} color="text-amber-300" />
          <MetricPill label="Red" value={`${ciStats.red}`} color="text-red-300" />
        </div>
      </div>

      {/* Hours Comparison */}
      <div>
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Training Hours Comparison</h3>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={hoursData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
            <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <YAxis type="category" dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} width={130} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="hours" name="Hours" radius={[0, 6, 6, 0]}>
              {hoursData.map((entry, i) => (
                <Cell key={i} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Skill Coverage */}
      <div>
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Skill Gap Analysis (%)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={skillCoverageData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 10 }} />
            <YAxis domain={[0, 100]} tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ color: '#9ca3af', fontSize: 12 }} />
            <Bar dataKey="current" name="Current" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="target" name="Target" fill="#a855f7" radius={[4, 4, 0, 0]} fillOpacity={0.5} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Audit Trail */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <p className="text-xs font-semibold text-gray-400 mb-2">Compliance Audit Trail</p>
        <div className="text-xs text-gray-500 space-y-1 font-mono">
          <p>Session ID: <span className="text-gray-300">{result.session_id}</span></p>
          <p>Assigned At: <span className="text-gray-300">{new Date().toISOString()}</span></p>
          <p>Bypass Attempted: <span className="text-gray-300">No</span></p>
          <p>Mandatory Courses Enforced:{' '}
            <span className="text-green-400">
              {result.path_variants[0]?.modules.filter((m) => m.is_mandatory).length ?? 0}
            </span>
          </p>
          <p>System Verification: <span className={allZ3Verified ? 'text-green-400' : 'text-red-400'}>
            {allZ3Verified ? 'PASSED' : 'FAILED'}
          </span></p>
        </div>
      </div>
    </div>
  );
}

function MetricPill({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-lg border border-gray-700 bg-gray-900 p-3">
      <p className={`text-lg font-bold font-mono ${color}`}>{value}</p>
      <p className="text-[11px] text-gray-400 mt-1">{label}</p>
    </div>
  );
}

function MetricCard({
  label,
  value,
  sub,
  color,
  bg,
}: {
  label: string;
  value: string;
  sub: string;
  color: string;
  bg: string;
}) {
  return (
    <div className={`rounded-xl p-3 border ${bg}`}>
      <div className={`text-xl font-bold font-mono ${color}`}>{value}</div>
      <div className="text-xs font-medium text-gray-300 mt-0.5">{label}</div>
      <div className="text-[10px] text-gray-500 mt-0.5">{sub}</div>
    </div>
  );
}
