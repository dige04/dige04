const fs = require('fs');

const NOW = new Date();
const HOUR = NOW.getUTCHours();

function getTimeGradient() {
  if (HOUR >= 5 && HOUR < 12) return { c1: '#0f2027', c2: '#2c5364', c3: '#203a43', label: 'morning' };
  if (HOUR >= 12 && HOUR < 17) return { c1: '#1a1a2e', c2: '#16213e', c3: '#0f3460', label: 'afternoon' };
  if (HOUR >= 17 && HOUR < 21) return { c1: '#0d1b2a', c2: '#1b263b', c3: '#415a77', label: 'evening' };
  return { c1: '#0a0a0a', c2: '#1a1a2e', c3: '#16213e', label: 'night' };
}

function getLightGradient() {
  if (HOUR >= 5 && HOUR < 12) return { c1: '#e0f7fa', c2: '#b2ebf2', c3: '#80deea', label: 'morning' };
  if (HOUR >= 12 && HOUR < 17) return { c1: '#e8eaf6', c2: '#c5cae9', c3: '#9fa8da', label: 'afternoon' };
  if (HOUR >= 17 && HOUR < 21) return { c1: '#fce4ec', c2: '#f8bbd0', c3: '#f48fb1', label: 'evening' };
  return { c1: '#f3e5f5', c2: '#e1bee7', c3: '#ce93d8', label: 'night' };
}

function generateSVG(mode = 'dark') {
  const isDark = mode === 'dark';
  const g = isDark ? getTimeGradient() : getLightGradient();
  const date = NOW.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });

  const colors = isDark
    ? { name: '#e6f1ff', tagline: '#8892b0', role: '#64ffda', time: '#4a5568', grid: '#fff', accent1: '#64ffda', accent2: '#48b1bf', dots: '#64ffda' }
    : { name: '#1a202c', tagline: '#4a5568', role: '#0d9488', time: '#94a3b8', grid: '#000', accent1: '#0d9488', accent2: '#14b8a6', dots: '#0d9488' };

  return `<svg width="800" height="220" viewBox="0 0 800 220" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${g.c1}"/>
      <stop offset="50%" stop-color="${g.c2}"/>
      <stop offset="100%" stop-color="${g.c3}"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="${colors.accent1}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="${colors.accent2}" stop-opacity="0.4"/>
    </linearGradient>
    ${isDark ? `<filter id="glow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>` : ''}
  </defs>

  <rect width="800" height="220" fill="url(#bg)" rx="8"/>

  <g opacity="0.04" stroke="${colors.grid}" stroke-width="0.5">
    ${Array.from({ length: 20 }, (_, i) => `<line x1="${i * 40}" y1="0" x2="${i * 40}" y2="220"/>`).join('\n    ')}
    ${Array.from({ length: 6 }, (_, i) => `<line x1="0" y1="${i * 40}" x2="800" y2="${i * 40}"/>`).join('\n    ')}
  </g>

  <rect x="60" y="155" width="120" height="2" fill="url(#accent)" rx="1"/>

  <text x="60" y="80" font-family="'Segoe UI', system-ui, -apple-system, sans-serif" font-size="38" font-weight="700" fill="${colors.name}"${isDark ? ' filter="url(#glow)"' : ''}>
    Hieu Dinh
  </text>

  <text x="60" y="115" font-family="'Segoe UI', system-ui, -apple-system, sans-serif" font-size="16" fill="${colors.tagline}" letter-spacing="0.5">
    Building with AI &amp; shipping things that matter
  </text>

  <text x="60" y="140" font-family="'Segoe UI', system-ui, -apple-system, sans-serif" font-size="13" fill="${colors.role}" letter-spacing="1">
    Full-Stack Engineer  ·  AI Builder  ·  Open Source
  </text>

  <text x="60" y="185" font-family="'SF Mono', 'Fira Code', monospace" font-size="11" fill="${colors.time}">
    last updated ${date} · ${g.label}
  </text>

  <g fill="${colors.dots}" opacity="0.15">
    <circle cx="700" cy="40" r="30"/>
    <circle cx="740" cy="90" r="15"/>
    <circle cx="680" cy="100" r="8"/>
  </g>
</svg>`;
}

fs.writeFileSync('header.svg', generateSVG('dark'));
fs.writeFileSync('header-light.svg', generateSVG('light'));
console.log('Generated header.svg + header-light.svg');
