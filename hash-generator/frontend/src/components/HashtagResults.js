// frontend/src/components/HashtagResults.js

import React, { useState } from 'react';
import PerformancePredictor from './PerformancePredictor';

function Chip({ item }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(item.tag);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  const colors = {
    trending: { bg: 'rgba(255,107,107,0.12)', border: 'rgba(255,107,107,0.35)', text: '#fca5a5' },
    broad:    { bg: 'rgba(78,205,196,0.12)',  border: 'rgba(78,205,196,0.35)',  text: '#6ee7b7' },
    niche:    { bg: 'rgba(167,139,250,0.12)', border: 'rgba(167,139,250,0.35)', text: '#c4b5fd' },
  };
  const c = colors[item.category] || colors.broad;
  return (
    <button
      className="chip"
      onClick={copy}
      title={`${item.label} · Score: ${item.score} · Click to copy`}
      style={{ background: c.bg, borderColor: c.border, color: c.text }}
    >
      <span className="chip-tag">{copied ? '✓ Copied!' : item.tag}</span>
      <span className="chip-meta">
        {item.source === 'realtime_trends' && <span className="live-dot" />}
        {item.score}
      </span>
    </button>
  );
}

const TABS = [
  { id: 'all',      label: '⚡ All'      },
  { id: 'trending', label: '🔥 Trending' },
  { id: 'broad',    label: '📈 Broad'    },
  { id: 'niche',    label: '🎯 Niche'    },
];

export default function HashtagResults({ result }) {
  const [activeTab,     setActiveTab]     = useState('all');
  const [copiedAll,     setCopiedAll]     = useState(false);
  const [copiedCaption, setCopiedCaption] = useState(false);
  const [showPredictor, setShowPredictor] = useState(false);

  if (!result) return null;

  const tabData = {
    all:      result.hashtags || [],
    trending: result.trending || [],
    broad:    result.broad    || [],
    niche:    result.niche    || [],
  };
  const displayed = tabData[activeTab] || [];

  const copyTab = () => {
    navigator.clipboard.writeText(displayed.map(h => h.tag).join(' '));
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 2000);
  };

  const copyCaption = () => {
    navigator.clipboard.writeText(result.caption_preview || '');
    setCopiedCaption(true);
    setTimeout(() => setCopiedCaption(false), 2000);
  };

  const hasPredictions = result.predictions &&
    result.predictions.predictions &&
    result.predictions.predictions.length > 0;

  return (
    <div className="results-panel">

      {/* Source + topics + keywords + predictor toggle */}
      <div className="results-top">
        <div className="source-area">
          <span className={`source-badge ${result.is_realtime ? 'live' : 'curated'}`}>
            {result.is_realtime
              ? `🟢 Live · ${result.trend_source}`
              : '⚪ Curated Data'}
          </span>
          {result.trend_fetched && (
            <span className="fetch-time">Updated: {result.trend_fetched}</span>
          )}
          {hasPredictions && (
            <button
              className={`pred-toggle-btn ${showPredictor ? 'active' : ''}`}
              onClick={() => setShowPredictor(!showPredictor)}
            >
              🎯 {showPredictor ? 'Hide Predictions' : 'Performance Predictions'}
            </button>
          )}
        </div>

        {result.topics && result.topics.length > 0 && (
          <div className="topics-row">
            <span className="topics-label">Topics:</span>
            {result.topics.map(t => <span key={t} className="topic-tag">{t}</span>)}
          </div>
        )}

        {result.keywords && result.keywords.length > 0 && (
          <div className="keywords-row">
            <span className="keywords-label">Keywords:</span>
            {result.keywords.map(k => <span key={k} className="keyword-tag">{k}</span>)}
          </div>
        )}
      </div>

      {/* Stats row */}
      <div className="stats-row">
        <div className="stat-box">
          <span className="stat-num">{result.total}</span>
          <span className="stat-lbl">Total</span>
        </div>
        <div className="stat-box trending-box">
          <span className="stat-num">{result.trending?.length || 0}</span>
          <span className="stat-lbl">🔥 Trending</span>
        </div>
        <div className="stat-box broad-box">
          <span className="stat-num">{result.broad?.length || 0}</span>
          <span className="stat-lbl">📈 Broad</span>
        </div>
        <div className="stat-box niche-box">
          <span className="stat-num">{result.niche?.length || 0}</span>
          <span className="stat-lbl">🎯 Niche</span>
        </div>
        <div className="stat-box">
          <span className="stat-num">{result.optimal_count}</span>
          <span className="stat-lbl">Optimal</span>
        </div>
      </div>

      {/* Platform tip */}
      {result.platform_tip && (
        <div className="platform-tip">
          💡 <strong>{result.platform}:</strong> {result.platform_tip}
        </div>
      )}

      {/* Performance Predictor inline */}
      {showPredictor && hasPredictions && (
        <PerformancePredictor predictions={result.predictions} />
      )}

      {/* Caption */}
      <div className="caption-box">
        <div className="caption-header">
          <span className="caption-label">📋 Caption Preview</span>
          <button className="copy-btn" onClick={copyCaption}>
            {copiedCaption ? '✓ Copied!' : '⎘ Copy Caption'}
          </button>
        </div>
        <p className="caption-text">{result.caption_preview}</p>
      </div>

      {/* Tabs */}
      <div className="tabs-bar">
        {TABS.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
            <span className="tab-count">{tabData[tab.id]?.length || 0}</span>
          </button>
        ))}
        <button className="copy-tab-btn" onClick={copyTab}>
          {copiedAll ? '✓ Copied!' : `⎘ Copy ${activeTab}`}
        </button>
      </div>

      {/* Chips */}
      <div className="chips-grid">
        {displayed.length > 0
          ? displayed.map((item, i) => <Chip key={i} item={item} />)
          : <p className="empty-msg">No hashtags in this category.</p>
        }
      </div>

      {/* Legend */}
      <div className="legend">
        <span className="legend-item"><span className="dot red"    /> Trending (≥75)</span>
        <span className="legend-item"><span className="dot green"  /> Broad (55–74)</span>
        <span className="legend-item"><span className="dot purple" /> Niche (&lt;55)</span>
        <span className="legend-item"><span className="live-dot"   /> Live trend</span>
        <span className="legend-tip">💡 Click any tag to copy</span>
      </div>
    </div>
  );
}