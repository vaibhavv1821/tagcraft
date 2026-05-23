// frontend/src/services/analytics.js
// ─────────────────────────────────────────────────────────────
// Analytics Engine — tracks hashtag generation history
// Storage: localStorage (no database, works offline)
//
// Data stored:
//   tagcraft_sessions  → array of generation sessions
//   tagcraft_tag_freq  → {tag: count} frequency map
//   tagcraft_platform  → {platform: count} usage map
// ─────────────────────────────────────────────────────────────

const KEYS = {
  SESSIONS:  'tagcraft_sessions',
  TAG_FREQ:  'tagcraft_tag_freq',
  PLATFORMS: 'tagcraft_platforms',
  META:      'tagcraft_meta',
};

const MAX_SESSIONS = 50; // keep last 50 sessions

// ── Helpers ──────────────────────────────────────────────────

function load(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function save(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.warn('[analytics] localStorage write failed:', e);
  }
}

// ── RECORD a generation session ───────────────────────────────
export function recordSession(result) {
  if (!result || !result.hashtags) return;

  const now = new Date();

  // ── 1. Save session ──
  const sessions = load(KEYS.SESSIONS, []);

  const session = {
    id:         Date.now(),
    timestamp:  now.toISOString(),
    date:       now.toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' }),
    time:       now.toLocaleTimeString('en-IN', { hour:'2-digit', minute:'2-digit' }),
    platform:   result.platform || 'all',
    text:       (result.input_text || '').slice(0, 80),
    total:      result.total || 0,
    trending:   result.trending?.length || 0,
    broad:      result.broad?.length    || 0,
    niche:      result.niche?.length    || 0,
    topTags:    (result.hashtags || []).slice(0, 5).map(h => h.tag),
    keywords:   result.keywords || [],
    isRealtime: result.is_realtime || false,
  };

  sessions.unshift(session);           // newest first
  save(KEYS.SESSIONS, sessions.slice(0, MAX_SESSIONS));

  // ── 2. Update tag frequency map ──
  const tagFreq = load(KEYS.TAG_FREQ, {});
  (result.hashtags || []).forEach(h => {
    const tag = h.tag;
    tagFreq[tag] = (tagFreq[tag] || 0) + 1;
  });
  save(KEYS.TAG_FREQ, tagFreq);

  // ── 3. Update platform usage ──
  const platforms = load(KEYS.PLATFORMS, {});
  const plat = result.platform || 'all';
  platforms[plat] = (platforms[plat] || 0) + 1;
  save(KEYS.PLATFORMS, platforms);

  // ── 4. Update meta counters ──
  const meta = load(KEYS.META, { totalGenerations: 0, totalHashtags: 0 });
  meta.totalGenerations += 1;
  meta.totalHashtags    += result.total || 0;
  meta.lastGenerated     = now.toISOString();
  save(KEYS.META, meta);
}

// ── GET all analytics data ────────────────────────────────────
export function getAnalytics() {
  const sessions  = load(KEYS.SESSIONS,  []);
  const tagFreq   = load(KEYS.TAG_FREQ,  {});
  const platforms = load(KEYS.PLATFORMS, {});
  const meta      = load(KEYS.META, { totalGenerations: 0, totalHashtags: 0 });

  // Top 10 tags sorted by frequency
  const topTags = Object.entries(tagFreq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([tag, count]) => ({ tag, count }));

  // Platform breakdown as array
  const platformBreakdown = Object.entries(platforms)
    .sort((a, b) => b[1] - a[1])
    .map(([platform, count]) => ({ platform, count }));

  // Category totals across all sessions
  const categoryTotals = sessions.reduce(
    (acc, s) => {
      acc.trending += s.trending || 0;
      acc.broad    += s.broad    || 0;
      acc.niche    += s.niche    || 0;
      return acc;
    },
    { trending: 0, broad: 0, niche: 0 }
  );

  // Generation frequency — last 7 sessions grouped by date
  const last7 = sessions.slice(0, 7).reverse();
  const genByDate = last7.map(s => ({
    date:  s.date,
    count: s.total || 0,
  }));

  return {
    meta,
    sessions:          sessions.slice(0, 10),   // last 10 for history table
    topTags,
    platformBreakdown,
    categoryTotals,
    genByDate,
    totalSessions:     sessions.length,
  };
}

// ── CLEAR all analytics ───────────────────────────────────────
export function clearAnalytics() {
  Object.values(KEYS).forEach(k => localStorage.removeItem(k));
}

// ── CHECK if any data exists ──────────────────────────────────
export function hasData() {
  const meta = load(KEYS.META, { totalGenerations: 0 });
  return meta.totalGenerations > 0;
}