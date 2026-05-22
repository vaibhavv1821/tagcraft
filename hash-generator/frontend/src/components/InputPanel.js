// frontend/src/components/InputPanel.js

import React from 'react';

const PLATFORMS = [
  { id: 'all',       label: 'All Platforms', icon: '🌐' },
  { id: 'instagram', label: 'Instagram',      icon: '📸' },
  { id: 'twitter',   label: 'Twitter / X',    icon: '𝕏'  },
  { id: 'linkedin',  label: 'LinkedIn',       icon: '💼' },
  { id: 'youtube',   label: 'YouTube',        icon: '▶'  },
  { id: 'github',    label: 'GitHub',         icon: '🐙' },
];

const COUNT_OPTIONS = [10, 15, 20, 30, 50];

const COUNTRY_OPTIONS = [
  { code: 'IN', label: '🇮🇳 India'     },
  { code: 'US', label: '🇺🇸 USA'       },
  { code: 'GB', label: '🇬🇧 UK'        },
  { code: 'AU', label: '🇦🇺 Australia' },
  { code: 'CA', label: '🇨🇦 Canada'    },
];

export default function InputPanel({
  text, setText,
  platform, setPlatform,
  count, setCount,
  country, setCountry,
  onGenerate, onReset,
  loading, hasResult,
}) {
  const wordCount  = text.trim() ? text.trim().split(/\s+/).length : 0;
  const canGenerate = text.trim().length >= 3 && !loading;

  return (
    <div className="input-panel">

      {/* Header */}
      <div className="ip-header">
        <h2 className="ip-title">✍ Describe Your Content</h2>
        <p className="ip-sub">
          Enter your post caption, topic, or project description
        </p>
      </div>

      {/* Platform pills */}
      <div className="platform-pills">
        {PLATFORMS.map(p => (
          <button
            key={p.id}
            className={`platform-pill ${platform === p.id ? 'active' : ''}`}
            onClick={() => setPlatform(p.id)}
            disabled={loading}
          >
            <span>{p.icon}</span>
            <span>{p.label}</span>
          </button>
        ))}
      </div>

      {/* Textarea */}
      <textarea
        className="main-textarea"
        rows={5}
        placeholder={
          `e.g. I built an open source REST API using Python Flask with Docker and GitHub Actions CI/CD...\n\nor: Just finished my workout — feeling amazing after leg day and nutrition prep!`
        }
        value={text}
        onChange={e => setText(e.target.value)}
        disabled={loading}
        spellCheck={false}
      />

      {/* Bottom controls */}
      <div className="ip-controls">

        {/* Left: word count + country */}
        <div className="ip-left">
          <span className="word-count">
            {wordCount} words · {text.length} chars
          </span>
          <select
            className="country-select"
            value={country}
            onChange={e => setCountry(e.target.value)}
            disabled={loading}
          >
            {COUNTRY_OPTIONS.map(c => (
              <option key={c.code} value={c.code}>{c.label}</option>
            ))}
          </select>
        </div>

        {/* Right: count + buttons */}
        <div className="ip-right">
          <div className="count-row">
            <span className="count-label">Count:</span>
            {COUNT_OPTIONS.map(n => (
              <button
                key={n}
                className={`count-btn ${count === n ? 'active' : ''}`}
                onClick={() => setCount(n)}
                disabled={loading}
              >
                {n}
              </button>
            ))}
          </div>

          <div className="btn-row">
            {hasResult && (
              <button className="btn btn-ghost" onClick={onReset}>
                ← New
              </button>
            )}
            <button
              className="btn btn-primary"
              onClick={onGenerate}
              disabled={!canGenerate}
            >
              {loading
                ? <><span className="spinner" /> Generating…</>
                : '# Generate Hashtags'
              }
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}