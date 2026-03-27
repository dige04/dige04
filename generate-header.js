const fs = require('fs');

function generateSVG(mode = 'dark') {
  const isDark = mode === 'dark';

  const bg = isDark ? '#0a0a0f' : '#f8f9fc';
  const scanLineColor = isDark ? '#fff' : '#000';
  const hexColor = isDark ? '#64ffda' : '#0d9488';
  const subtitleColor = isDark ? '#8892b0' : '#64748b';

  // Neon gradient stops (same for both modes, looks great on both)
  const gradStops = isDark
    ? [
        { offset: '0%', color: '#ff6b9d' },
        { offset: '25%', color: '#c084fc' },
        { offset: '50%', color: '#22d3ee' },
        { offset: '75%', color: '#a78bfa' },
        { offset: '100%', color: '#34d399' },
      ]
    : [
        { offset: '0%', color: '#7c3aed' },
        { offset: '25%', color: '#2563eb' },
        { offset: '50%', color: '#0891b2' },
        { offset: '75%', color: '#059669' },
        { offset: '100%', color: '#0d9488' },
      ];

  // Hexagon path (centered at 0,0, radius ~20)
  const hex = (cx, cy, r) => {
    const pts = Array.from({ length: 6 }, (_, i) => {
      const a = (Math.PI / 3) * i - Math.PI / 6;
      return `${cx + r * Math.cos(a)},${cy + r * Math.sin(a)}`;
    });
    return pts.join(' ');
  };

  // Deterministic "random" positions for hexagons
  const hexagons = [
    { cx: 620, cy: 35, r: 18, opacity: 0.08, delay: '0s' },
    { cx: 680, cy: 80, r: 12, opacity: 0.06, delay: '0.5s' },
    { cx: 720, cy: 45, r: 25, opacity: 0.05, delay: '1s' },
    { cx: 660, cy: 120, r: 10, opacity: 0.07, delay: '1.5s' },
    { cx: 750, cy: 100, r: 15, opacity: 0.04, delay: '0.8s' },
    { cx: 580, cy: 90, r: 8, opacity: 0.06, delay: '2s' },
    { cx: 770, cy: 160, r: 20, opacity: 0.05, delay: '0.3s' },
    { cx: 550, cy: 160, r: 14, opacity: 0.04, delay: '1.2s' },
  ];

  // Data stream columns
  const streams = [
    { x: 500, chars: '01101001', delay: '0s' },
    { x: 540, chars: '10110100', delay: '0.7s' },
    { x: 570, chars: '01001101', delay: '1.4s' },
  ];

  return `<svg width="800" height="200" viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="neon" x1="0%" y1="0%" x2="100%" y2="0%">
      ${gradStops.map((s) => `<stop offset="${s.offset}" stop-color="${s.color}"/>`).join('\n      ')}
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="softglow">
      <feGaussianBlur stdDeviation="1.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <style>
      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
      }
      @keyframes pulse {
        0%, 100% { opacity: 0.03; }
        50% { opacity: 0.08; }
      }
      @keyframes stream {
        0% { transform: translateY(-30px); opacity: 0; }
        20% { opacity: 0.15; }
        80% { opacity: 0.15; }
        100% { transform: translateY(200px); opacity: 0; }
      }
      @keyframes glitch {
        0%, 90%, 100% { transform: translate(0); }
        92% { transform: translate(-2px, 1px); }
        94% { transform: translate(2px, -1px); }
        96% { transform: translate(-1px, -1px); }
        98% { transform: translate(1px, 1px); }
      }
      .hex { animation: float 4s ease-in-out infinite; }
      .scan { animation: pulse 3s ease-in-out infinite; }
      .data { animation: stream 3s linear infinite; }
      .title { animation: glitch 8s ease-in-out infinite; }
    </style>
  </defs>

  <!-- Background -->
  <rect width="800" height="200" fill="${bg}"/>

  <!-- Scan lines (CRT effect) -->
  <g class="scan">
    ${Array.from({ length: 50 }, (_, i) => `<line x1="0" y1="${i * 4}" x2="800" y2="${i * 4}" stroke="${scanLineColor}" stroke-width="0.3" opacity="0.03"/>`).join('\n    ')}
  </g>

  <!-- Floating hexagons -->
  ${hexagons
    .map(
      (h) =>
        `<polygon class="hex" points="${hex(h.cx, h.cy, h.r)}" fill="none" stroke="${hexColor}" stroke-width="1" opacity="${h.opacity}" style="animation-delay: ${h.delay}"/>`
    )
    .join('\n  ')}

  <!-- Data streams -->
  ${streams
    .map(
      (s) =>
        `<g class="data" style="animation-delay: ${s.delay}; animation-duration: ${2 + Math.random()}s">
      ${s.chars
        .split('')
        .map(
          (c, i) =>
            `<text x="${s.x}" y="${i * 18}" font-family="'SF Mono', 'Fira Code', monospace" font-size="10" fill="${hexColor}" opacity="0.12">${c}</text>`
        )
        .join('\n      ')}
    </g>`
    )
    .join('\n  ')}

  <!-- Name with neon gradient -->
  <g class="title" filter="${isDark ? 'url(#glow)' : 'url(#softglow)'}">
    <text x="55" y="85" font-family="'Segoe UI', system-ui, -apple-system, sans-serif" font-size="52" font-weight="800" fill="url(#neon)" letter-spacing="-1">
      HIEU DINH
    </text>
  </g>

  <!-- Subtitle -->
  <text x="58" y="120" font-family="'Segoe UI', system-ui, -apple-system, sans-serif" font-size="15" fill="${subtitleColor}" letter-spacing="0.5">
    Build from scratch. Understand deeply. Ship relentlessly.
  </text>

  <!-- Accent line under subtitle -->
  <rect x="58" y="132" width="80" height="2" fill="url(#neon)" rx="1" opacity="0.6"/>

  <!-- Role tags -->
  <g font-family="'SF Mono', 'Fira Code', monospace" font-size="11" letter-spacing="0.5">
    <text x="58" y="160" fill="${hexColor}" opacity="0.7">AI Engineer</text>
    <text x="155" y="160" fill="${subtitleColor}" opacity="0.4">·</text>
    <text x="170" y="160" fill="${hexColor}" opacity="0.7">Full-Stack Dev</text>
    <text x="290" y="160" fill="${subtitleColor}" opacity="0.4">·</text>
    <text x="305" y="160" fill="${hexColor}" opacity="0.7">Open Source</text>
  </g>
</svg>`;
}

fs.writeFileSync('header.svg', generateSVG('dark'));
fs.writeFileSync('header-light.svg', generateSVG('light'));
console.log('Generated header.svg + header-light.svg');
