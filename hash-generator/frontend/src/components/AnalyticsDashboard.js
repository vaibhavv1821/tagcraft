// frontend/src/components/AnalyticsDashboard.js
// ─────────────────────────────────────────────────────────────
// Analytics Dashboard — shows generation history, top tags,
// platform breakdown, category distribution
// Uses localStorage — no database needed
// ─────────────────────────────────────────────────────────────

import React, { useState, useEffect, useRef } from 'react';
import { getAnalytics, clearAnalytics, hasData } from '../services/analytics';

// ── PLATFORM META ─────────────────────────────────────────────
const PLATFORM_META = {
  all:       { label: 'All',       icon: '🌐', color: '#4f8ef7' },
  instagram: { label: 'Instagram', icon: '📸', color: '#e1306c' },
  twitter:   { label: 'Twitter/X', icon: '𝕏',  color: '#1da1f2' },
  linkedin:  { label: 'LinkedIn',  icon: '💼', color: '#0077b5' },
  youtube:   { label: 'YouTube',   icon: '▶',  color: '#ff0000' },
  github:    { label: 'GitHub',    icon: '🐙', color: '#6e40c9' },
};

// ── MINI BAR CHART ────────────────────────────────────────────
function BarChart({ data, maxVal }) {
  if (!data || data.length === 0) return <p className="an-empty">No tag data yet.</p>;
  const max = maxVal || Math.max(...data.map(d => d.count), 1);

  return (
    <div className="bar-chart">
      {data.map((item, i) => {
        const pct = Math.max(4, (item.count / max) * 100);
        return (
          <div key={i} className="bar-row" style={{ animationDelay: `${i * 0.05}s` }}>
            <span className="bar-label" title={item.tag}>{item.tag}</span>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="bar-val">{item.count}</span>
          </div>
        );
      })}
    </div>
  );
}

// ── DONUT CHART (SVG) ─────────────────────────────────────────
function DonutChart({ data }) {
  if (!data || data.length === 0) return <p className="an-empty">No platform data yet.</p>;

  const total = data.reduce((s, d) => s + d.count, 0);
  if (total === 0) return <p className="an-empty">No platform data yet.</p>;

  const size   = 160;
  const cx     = size / 2;
  const cy     = size / 2;
  const radius = 58;
  const stroke = 22;

  // Build arc segments
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  const segments = data.map((d, i) => {
    const meta  = PLATFORM_META[d.platform] || PLATFORM_META.all;
    const pct   = d.count / total;
    const dash  = pct * circumference;
    const gap   = circumference - dash;
    const seg   = { ...d, meta, dash, gap, offset, pct };
    offset += dash;
    return seg;
  });

  return (
    <div className="donut-wrap">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background circle */}
        <circle cx={cx} cy={cy} r={radius}
          fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={stroke} />

        {/* Segments */}
        {segments.map((seg, i) => (
          <circle
            key={i}
            cx={cx} cy={cy} r={radius}
            fill="none"
            stroke={seg.meta.color}
            strokeWidth={stroke}
            strokeDasharray={`${seg.dash} ${seg.gap}`}
            strokeDashoffset={-seg.offset}
            strokeLinecap="butt"
            transform={`rotate(-90 ${cx} ${cy})`}
            style={{ opacity: 0.85, transition: 'stroke-dasharray .6s ease' }}
          />
        ))}

        {/* Center text */}
        <text x={cx} y={cy - 6} textAnchor="middle"
          fontSize="22" fontWeight="800" fill="#f0f2f8"
          fontFamily="'JetBrains Mono', monospace">
          {total}
        </text>
        <text x={cx} y={cy + 12} textAnchor="middle"
          fontSize="9" fill="#4a5568"
          fontFamily="'Plus Jakarta Sans', sans-serif"
          fontWeight="600" letterSpacing="1">
          TOTAL
        </text>
      </svg>

      {/* Legend */}
      <div className="donut-legend">
        {segments.map((seg, i) => (
          <div key={i} className="donut-legend-item">
            <span className="donut-dot" style={{ background: seg.meta.color }} />
            <span className="donut-plat">{seg.meta.icon} {seg.meta.label}</span>
            <span className="donut-count">{seg.count}</span>
            <span className="donut-pct">{Math.round(seg.pct * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── CATEGORY RING ─────────────────────────────────────────────
function CategoryBars({ totals }) {
  const total = (totals.trending + totals.broad + totals.niche) || 1;
  const cats  = [
    { label: 'Trending', val: totals.trending, color: '#ff6b6b', pct: totals.trending / total },
    { label: 'Broad',    val: totals.broad,    color: '#4ecdc4', pct: totals.broad    / total },
    { label: 'Niche',    val: totals.niche,    color: '#a78bfa', pct: totals.niche    / total },
  ];

  return (
    <div className="cat-bars">
      {/* Segmented bar */}
      <div className="cat-track">
        {cats.map((c, i) => (
          <div
            key={i}
            className="cat-segment"
            style={{ width: `${c.pct * 100}%`, background: c.color }}
            title={`${c.label}: ${c.val}`}
          />
        ))}
      </div>
      {/* Labels */}
      <div className="cat-labels">
        {cats.map((c, i) => (
          <div key={i} className="cat-label-item">
            <span className="cat-dot" style={{ background: c.color }} />
            <span className="cat-name">{c.label}</span>
            <span className="cat-num">{c.val}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── HISTORY TABLE ─────────────────────────────────────────────
function HistoryTable({ sessions }) {
  if (!sessions || sessions.length === 0) {
    return <p className="an-empty">No sessions yet. Generate some hashtags!</p>;
  }

  return (
    <div className="history-table-wrap">
      <table className="history-table">
        <thead>
          <tr>
            <th>Date & Time</th>
            <th>Platform</th>
            <th>Input</th>
            <th>Total</th>
            <th>🔥</th>
            <th>📈</th>
            <th>🎯</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map((s, i) => {
            const meta = PLATFORM_META[s.platform] || PLATFORM_META.all;
            return (
              <tr key={s.id} style={{ animationDelay: `${i * 0.04}s` }}>
                <td className="td-date">
                  <span className="td-dateval">{s.date}</span>
                  <span className="td-time">{s.time}</span>
                </td>
                <td className="td-plat">
                  <span className="plat-pill" style={{ borderColor: meta.color + '55', color: meta.color }}>
                    {meta.icon} {meta.label}
                  </span>
                </td>
                <td className="td-text" title={s.text}>
                  {s.text.length > 40 ? s.text.slice(0, 40) + '…' : s.text}
                </td>
                <td className="td-num td-total">{s.total}</td>
                <td className="td-num td-fire">{s.trending}</td>
                <td className="td-num td-broad">{s.broad}</td>
                <td className="td-num td-niche">{s.niche}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ── MINI LINE SPARKLINE ───────────────────────────────────────
function Sparkline({ data }) {
  if (!data || data.length < 2) return null;
  const vals   = data.map(d => d.count);
  const max    = Math.max(...vals, 1);
  const min    = 0;
  const w      = 200;
  const h      = 48;
  const pts    = vals.map((v, i) => {
    const x = (i / (vals.length - 1)) * w;
    const y = h - ((v - min) / (max - min)) * (h - 8) - 4;
    return `${x},${y}`;
  });
  const path   = `M ${pts.join(' L ')}`;
  const area   = `M ${pts[0]} L ${pts.join(' L ')} L ${w},${h} L 0,${h} Z`;

  return (
    <div className="sparkline-wrap">
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
        <defs>
          <linearGradient id="spk-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#4f8ef7" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#4f8ef7" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={area} fill="url(#spk-grad)" />
        <path d={path} fill="none" stroke="#4f8ef7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        {vals.map((v, i) => {
          const [x, y] = pts[i].split(',').map(Number);
          return <circle key={i} cx={x} cy={y} r="3" fill="#4f8ef7" />;
        })}
      </svg>
      <div className="sparkline-labels">
        {data.map((d, i) => (
          <span key={i} className="spk-label">{d.date?.split(' ')[0]}</span>
        ))}
      </div>
    </div>
  );
}

// ── MAIN DASHBOARD COMPONENT ──────────────────────────────────
export default function AnalyticsDashboard({ onClose }) {
  const [data,     setData]     = useState(null);
  const [clearing, setClearing] = useState(false);

  const load = () => setData(getAnalytics());

  useEffect(() => { load(); }, []);

  const handleClear = () => {
    if (!window.confirm('Clear all analytics data? This cannot be undone.')) return;
    setClearing(true);
    clearAnalytics();
    setTimeout(() => { load(); setClearing(false); }, 400);
  };

  if (!data) return null;

  const noData = data.totalSessions === 0;

  return (
    <div className="an-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="an-modal">

        {/* ── Header ── */}
        <div className="an-header">
          <div className="an-header-left">
            <div className="an-icon">📊</div>
            <div>
              <h2 className="an-title">Analytics Dashboard</h2>
              <p className="an-sub">Your hashtag generation insights</p>
            </div>
          </div>
          <div className="an-header-right">
            {!noData && (
              <button
                className="an-clear-btn"
                onClick={handleClear}
                disabled={clearing}
              >
                {clearing ? '⟳ Clearing…' : '🗑 Clear Data'}
              </button>
            )}
            <button className="an-close-btn" onClick={onClose}>✕</button>
          </div>
        </div>

        {/* ── No data state ── */}
        {noData ? (
          <div className="an-no-data">
            <div className="an-no-data-icon">📈</div>
            <h3>No data yet</h3>
            <p>Generate some hashtags to start tracking your analytics!</p>
            <button className="btn btn-primary" onClick={onClose}>
              # Generate Hashtags
            </button>
          </div>
        ) : (
          <div className="an-body">

            {/* ── KPI Cards ── */}
            <div className="an-kpis">
              <div className="an-kpi">
                <span className="an-kpi-val">{data.meta.totalGenerations}</span>
                <span className="an-kpi-lbl">Total Sessions</span>
              </div>
              <div className="an-kpi">
                <span className="an-kpi-val">{data.meta.totalHashtags}</span>
                <span className="an-kpi-lbl">Tags Generated</span>
              </div>
              <div className="an-kpi">
                <span className="an-kpi-val">{data.topTags.length}</span>
                <span className="an-kpi-lbl">Unique Tags</span>
              </div>
              <div className="an-kpi">
                <span className="an-kpi-val">
                  {data.platformBreakdown[0]
                    ? (PLATFORM_META[data.platformBreakdown[0].platform]?.icon || '🌐') + ' ' +
                      (PLATFORM_META[data.platformBreakdown[0].platform]?.label || 'All')
                    : '—'}
                </span>
                <span className="an-kpi-lbl">Top Platform</span>
              </div>
            </div>

            {/* ── Charts row ── */}
            <div className="an-charts">

              {/* Top Tags Bar Chart */}
              <div className="an-card an-card-wide">
                <div className="an-card-header">
                  <h3 className="an-card-title">🏆 Top Hashtags</h3>
                  <span className="an-card-sub">by generation frequency</span>
                </div>
                <BarChart data={data.topTags} />
              </div>

              {/* Platform Donut */}
              <div className="an-card">
                <div className="an-card-header">
                  <h3 className="an-card-title">📡 Platform Usage</h3>
                  <span className="an-card-sub">breakdown</span>
                </div>
                <DonutChart data={data.platformBreakdown} />
              </div>

            </div>

            {/* ── Category + Sparkline row ── */}
            <div className="an-charts">

              {/* Category Distribution */}
              <div className="an-card">
                <div className="an-card-header">
                  <h3 className="an-card-title">🎯 Category Mix</h3>
                  <span className="an-card-sub">trending vs broad vs niche</span>
                </div>
                <CategoryBars totals={data.categoryTotals} />
              </div>

              {/* Sparkline */}
              {data.genByDate.length >= 2 && (
                <div className="an-card">
                  <div className="an-card-header">
                    <h3 className="an-card-title">📈 Generation Trend</h3>
                    <span className="an-card-sub">last sessions</span>
                  </div>
                  <Sparkline data={data.genByDate} />
                </div>
              )}
            </div>

            {/* ── History Table ── */}
            <div className="an-card an-card-full">
              <div className="an-card-header">
                <h3 className="an-card-title">🕒 Recent Sessions</h3>
                <span className="an-card-sub">last {data.sessions.length} generations</span>
              </div>
              <HistoryTable sessions={data.sessions} />
            </div>

          </div>
        )}
      </div>
    </div>
  );
}