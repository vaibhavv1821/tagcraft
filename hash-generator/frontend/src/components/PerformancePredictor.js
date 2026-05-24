// frontend/src/components/PerformancePredictor.js

import React, { useState } from 'react';

function GradeBadge({ grade, color, size = 'md' }) {
  const sizes = {
    sm: { width: 28, height: 28, font: 11 },
    md: { width: 38, height: 38, font: 14 },
    lg: { width: 52, height: 52, font: 20 },
  };
  const s = sizes[size] || sizes.md;
  return (
    <div style={{
      width: s.width, height: s.height, fontSize: s.font,
      background: `${color}18`, border: `1.5px solid ${color}55`,
      color: color, borderRadius: 8,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, flexShrink: 0,
    }}>
      {grade}
    </div>
  );
}

function MetricPill({ icon, label, value, accent }) {
  return (
    <div className="metric-pill" style={{ borderColor: accent + '30' }}>
      <span className="metric-icon">{icon}</span>
      <div className="metric-body">
        <span className="metric-val" style={{ color: accent }}>{value}</span>
        <span className="metric-lbl">{label}</span>
      </div>
    </div>
  );
}

function ScoreBar({ value, color, label }) {
  return (
    <div className="score-bar-row">
      <span className="score-bar-label">{label}</span>
      <div className="score-bar-track">
        <div className="score-bar-fill" style={{ width: `${value}%`, background: color }} />
      </div>
      <span className="score-bar-val">{value}</span>
    </div>
  );
}

function PredictionCard({ pred, index }) {
  const [expanded, setExpanded] = useState(false);

  const competitionColor = {
    'Very High':   '#ff6b6b',
    'High':        '#fb923c',
    'Medium-High': '#facc15',
    'Medium':      '#4ecdc4',
    'Low-Medium':  '#60a5fa',
    'Low':         '#a78bfa',
    'Very Low':    '#94a3b8',
  }[pred.competition] || '#94a3b8';

  return (
    <div
      className={`pred-card ${expanded ? 'expanded' : ''}`}
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      {/* Card header */}
      <div className="pred-card-head" onClick={() => setExpanded(!expanded)}>
        <div className="pred-left">
          <span className="pred-rank">#{index + 1}</span>
          <GradeBadge grade={pred.grade} color={pred.grade_color} size="md" />
          <div className="pred-tag-info">
            <span className="pred-tag">{pred.tag}</span>
            <span className="pred-reach-label">{pred.reach_label}</span>
          </div>
        </div>
        <div className="pred-right">
          <div className="pred-metric-row">
            <span className="pred-metric-item">
              <span className="pm-icon">👁</span>
              <span className="pm-val">{pred.reach_range}</span>
            </span>
            <span className="pred-metric-item">
              <span className="pm-icon">💬</span>
              <span className="pm-val">{pred.engagement_rate}</span>
            </span>
            <span
              className="pred-metric-item competition-pill"
              style={{
                color: competitionColor,
                borderColor: competitionColor + '40',
                background:  competitionColor + '12'
              }}
            >
              {pred.competition}
            </span>
          </div>
          <span className="pred-toggle">{expanded ? '▲' : '▼'}</span>
        </div>
      </div>

      {/* Expanded detail */}
      {expanded && (
        <div className="pred-detail">
          <div className="pred-scores">
            <ScoreBar value={pred.score}        color="#4f8ef7"        label="Popularity"    />
            <ScoreBar value={pred.platform_fit} color="#a78bfa"        label="Platform Fit"  />
            <ScoreBar value={pred.length_score} color="#4ecdc4"        label="Length Score"  />
            <ScoreBar value={pred.overall}      color={pred.grade_color} label="Overall"     />
          </div>

          <div className="pred-stats">
            <div className="pred-stat">
              <span className="ps-val">{pred.tag_length}</span>
              <span className="ps-lbl">Characters</span>
            </div>
            <div className="pred-stat">
              <span className="ps-val">{pred.length_note}</span>
              <span className="ps-lbl">Length</span>
            </div>
            <div className="pred-stat">
              <span className="ps-val">{pred.best_time}</span>
              <span className="ps-lbl">Best Time</span>
            </div>
            <div className="pred-stat">
              <span className="ps-val">{pred.best_days?.join(', ')}</span>
              <span className="ps-lbl">Best Days</span>
            </div>
          </div>

          {pred.tips && pred.tips.length > 0 && (
            <div className="pred-tips">
              {pred.tips.map((tip, i) => (
                <div key={i} className="pred-tip">
                  <span className="pred-tip-icon">💡</span>
                  <span>{tip}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SummaryBanner({ summary }) {
  if (!summary || !summary.avg_grade) return null;
  return (
    <div className="pred-summary">
      <div className="pred-sum-grade">
        <GradeBadge grade={summary.avg_grade} color={summary.avg_grade_color} size="lg" />
        <div>
          <div className="pred-sum-title">Overall Score</div>
          <div className="pred-sum-sub">{summary.avg_overall}/100 average</div>
        </div>
      </div>

      <div className="pred-sum-stats">
        <MetricPill icon="💬" label="Avg Engagement" value={summary.avg_engagement} accent="#4ecdc4" />
        <MetricPill icon="⏰" label="Best Time"      value={summary.best_time}      accent="#a78bfa" />
        <MetricPill icon="🏆" label="Top Tag"        value={summary.top_tag}        accent="#4f8ef7" />
      </div>

      <div className="pred-sum-grades">
        {Object.entries(summary.grade_counts || {}).map(([g, c]) => (
          c > 0 && (
            <div key={g} className="grade-count-pill">
              <span className="gc-grade">{g}</span>
              <span className="gc-count">{c}</span>
            </div>
          )
        ))}
      </div>

      {summary.mix_tip && (
        <div className="pred-mix-tip">
          <span>🎯</span> {summary.mix_tip}
        </div>
      )}

      {summary.best_days && (
        <div className="pred-best-days">
          <span className="pbd-label">📅 Best days:</span>
          {summary.best_days.map(d => (
            <span key={d} className="pbd-day">{d}</span>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PerformancePredictor({ predictions }) {
  const [showAll, setShowAll] = useState(false);

  if (!predictions || !predictions.predictions || predictions.predictions.length === 0) {
    return null;
  }

  const { predictions: preds, summary } = predictions;
  const displayed = showAll ? preds : preds.slice(0, 5);

  return (
    <div className="predictor-panel">
      <div className="predictor-header">
        <div className="predictor-title-row">
          <span className="predictor-icon">🎯</span>
          <div>
            <h3 className="predictor-title">Performance Predictor</h3>
            <p className="predictor-sub">
              Estimated reach & engagement for your top {preds.length} hashtags
            </p>
          </div>
        </div>
      </div>

      <SummaryBanner summary={summary} />

      <div className="pred-cards">
        {displayed.map((pred, i) => (
          <PredictionCard key={pred.tag} pred={pred} index={i} />
        ))}
      </div>

      {preds.length > 5 && (
        <button className="pred-show-more" onClick={() => setShowAll(!showAll)}>
          {showAll ? '▲ Show less' : `▼ Show all ${preds.length} predictions`}
        </button>
      )}
    </div>
  );
}