// frontend/src/App.js

import React, { useState, useEffect } from 'react';
import InputPanel          from './components/InputPanel';
import HashtagResults      from './components/HashtagResults';
import TrendingPanel       from './components/TrendingPanel';
import AnalyticsDashboard  from './components/AnalyticsDashboard';
import { generateHashtags, getTrending, checkHealth } from './services/api';
import { recordSession, hasData }                     from './services/analytics';
import './App.css';

export default function App() {
  const [text,        setText]        = useState('');
  const [platform,    setPlatform]    = useState('all');
  const [count,       setCount]       = useState(20);
  const [country,     setCountry]     = useState('IN');
  const [result,      setResult]      = useState(null);
  const [trending,    setTrending]    = useState([]);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState('');
  const [apiOk,       setApiOk]       = useState(null);
  const [isRealtime,  setIsRealtime]  = useState(false);
  const [showAnalytics,     setShowAnalytics]     = useState(false);
  const [analyticsHasData,  setAnalyticsHasData]  = useState(false);

  useEffect(() => {
    checkHealth().then(ok => {
      setApiOk(ok);
      if (ok) loadTrending('all', 'IN');
    });
    setAnalyticsHasData(hasData());
  }, []);

  const loadTrending = async (plat, ctry, kw = '') => {
    try {
      const data = await getTrending(plat, ctry, kw);
      setTrending(data.trending || []);
      setIsRealtime(data.is_realtime || false);
    } catch {}
  };

  const handlePlatformChange = (p) => {
    setPlatform(p);
    loadTrending(p, country);
  };

  const handleGenerate = async () => {
    if (!text.trim() || text.trim().length < 3) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await generateHashtags({ text, platform, count, country });
      setResult(data);
      recordSession(data);
      setAnalyticsHasData(true);
      if (data.keywords && data.keywords[0]) {
        loadTrending(platform, country, data.keywords[0]);
      }
    } catch (err) {
      setError(err.message || 'Something went wrong. Is Flask running?');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setText('');
    setError('');
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-icon">#</div>
            <div>
              <h1 className="brand-name">TagCraft</h1>
              <p className="brand-sub">AI-Powered Hashtag Generator · Real-Time Trends</p>
            </div>
          </div>
          <div className="header-right">
            <button
              className={`analytics-btn ${analyticsHasData ? 'has-data' : ''}`}
              onClick={() => setShowAnalytics(true)}
              title="View Analytics Dashboard"
            >
              <span className="analytics-btn-icon">📊</span>
              <span className="analytics-btn-label">Analytics</span>
              {analyticsHasData && <span className="analytics-dot" />}
            </button>
            <div className={`realtime-badge ${isRealtime ? 'live' : 'static'}`}>
              {isRealtime ? '🟢 Live Trends' : '⚪ Curated Data'}
            </div>
            <div className={`api-status ${apiOk === null ? 'pending' : apiOk ? 'ok' : 'err'}`}>
              <span className="api-dot" />
              <span>{apiOk === null ? 'Connecting…' : apiOk ? 'API Online' : 'API Offline'}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="main">
        <div className="layout">
          <div className="col-left">
            <InputPanel
              text={text}         setText={setText}
              platform={platform} setPlatform={handlePlatformChange}
              count={count}       setCount={setCount}
              country={country}   setCountry={setCountry}
              onGenerate={handleGenerate}
              onReset={handleReset}
              loading={loading}
              hasResult={!!result}
            />
            {error && <div className="error-banner">⚠ {error}</div>}
            {result && <HashtagResults result={result} />}
          </div>
          <div className="col-right">
            <TrendingPanel
              trending={trending}
              platform={platform}
              onPlatformChange={handlePlatformChange}
              isRealtime={isRealtime}
            />
          </div>
        </div>
      </main>

      <footer className="footer">
        TagCraft v2.0 · NLP + Google Trends · Instagram · Twitter/X · LinkedIn · YouTube · GitHub
      </footer>

      {showAnalytics && (
        <AnalyticsDashboard onClose={() => {
          setShowAnalytics(false);
          setAnalyticsHasData(hasData());
        }} />
      )}
    </div>
  );
}