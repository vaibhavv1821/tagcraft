// frontend/src/services/api.js

const BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export async function generateHashtags({ text, platform, count, country = 'IN' }) {
  const res = await fetch(`${BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, platform, count, country }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Failed to generate');
  return data;
}

export async function getTrending(platform = 'all', country = 'IN', keyword = '') {
  const params = new URLSearchParams({ platform, country });
  if (keyword) params.append('keyword', keyword);
  const res = await fetch(`${BASE}/trending?${params}`);
  const data = await res.json();
  if (!res.ok) throw new Error('Failed to fetch trending');
  return data;
}

export async function checkHealth() {
  try {
    const res = await fetch(`${BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}