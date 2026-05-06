/**
 * ORION Architekt-AT — Digital Art Hero
 * ════════════════════════════════════════
 * Isometrisches Architektur-Netz mit Alpiner Silhouette, Datenstrom-Partikeln
 * und ORION-Signet. Rein in Canvas — keine Abhängigkeiten.
 *
 * Farben & Ästhetik: AT-Bau trifft Cyberpunk-Blueprint.
 */

(function () {
  'use strict';

  // ─── Canvas-Setup ──────────────────────────────────────────────────────────
  const canvas = document.getElementById('orion-art-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, dpr;

  function resize() {
    dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    W = rect.width;
    H = rect.height;
    canvas.width  = W * dpr;
    canvas.height = H * dpr;
    ctx.scale(dpr, dpr);
  }
  resize();
  window.addEventListener('resize', () => { resize(); initScene(); });

  // ─── Farbpalette ───────────────────────────────────────────────────────────
  const C = {
    bg:        '#0a0f1e',
    gridLine:  'rgba(37,99,235,0.18)',
    gridGlow:  'rgba(37,99,235,0.55)',
    buildFill: 'rgba(15,25,60,0.85)',
    buildEdge: 'rgba(56,130,255,0.9)',
    buildTop:  'rgba(37,80,200,0.7)',
    buildWin:  'rgba(100,180,255,0.6)',
    dataBlue:  '#60a5fa',
    dataGreen: '#4ade80',
    dataPurple:'#a78bfa',
    dataOrange:'#fbbf24',
    signet:    'rgba(96,165,250,0.22)',
    signetGlow:'rgba(96,165,250,0.7)',
    alpine:    'rgba(30,50,110,0.6)',
    alpineEdge:'rgba(56,130,255,0.35)',
    fog:       'rgba(10,15,30,0.4)',
    scanline:  'rgba(37,99,235,0.025)',
  };

  // ─── Isometrische Hilfsfunktionen ──────────────────────────────────────────
  const ISO_ANG = Math.PI / 6;
  const ISO_SX  = Math.cos(ISO_ANG);
  const ISO_SY  = Math.sin(ISO_ANG);

  function iso(gx, gy) {
    return {
      x: (gx - gy) * ISO_SX,
      y: (gx + gy) * ISO_SY,
    };
  }

  // ─── Szene ─────────────────────────────────────────────────────────────────
  const GRID = 14;       // Gitterpunkte
  const CELL = 36;       // Zellgröße px (Screen)
  let OX, OY;            // Ursprung (Screen)

  function initOrigin() {
    OX = W * 0.5;
    OY = H * 0.60;
  }

  // Gebäude: {gx, gy, h, winRows, winCols, pulse}
  let buildings = [];
  // Verbindungen: {ax, ay, bx, by, progress, speed, color}
  let connections = [];
  // Partikel: {x,y,vx,vy,life,maxLife,r,color}
  let particles = [];
  // Signet-Rotationswinkel
  let signetAngle = 0;

  const BUILDING_POSITIONS = [
    [3,3,4],[3,5,3],[3,7,5],[3,9,2],
    [5,3,2],[5,5,6],[5,7,3],[5,9,4],
    [7,3,5],[7,5,2],[7,7,7],[7,9,2],
    [9,3,3],[9,5,4],[9,7,2],[9,9,5],
    [6,6,8],  // Hochhaus in der Mitte
  ];

  function initScene() {
    initOrigin();
    buildings = BUILDING_POSITIONS.map(([gx, gy, h]) => ({
      gx, gy, h,
      winRows: Math.max(1, h - 1),
      winCols: 2,
      pulse: Math.random() * Math.PI * 2,
    }));
    connections = [];
    particles = [];
    // Verbindungslinien zwischen benachbarten Gebäuden
    for (let i = 0; i < buildings.length; i++) {
      for (let j = i + 1; j < buildings.length; j++) {
        const a = buildings[i], b = buildings[j];
        const dist = Math.hypot(a.gx - b.gx, a.gy - b.gy);
        if (dist <= 3 && Math.random() < 0.55) {
          connections.push({
            ax: a.gx, ay: a.gy,
            bx: b.gx, by: b.gy,
            progress: Math.random(),
            speed: 0.003 + Math.random() * 0.004,
            color: [C.dataBlue, C.dataGreen, C.dataPurple, C.dataOrange][Math.floor(Math.random() * 4)],
          });
        }
      }
    }
  }

  // ─── Gebäude zeichnen ──────────────────────────────────────────────────────

  function toScreen(gx, gy) {
    const p = iso(gx, gy);
    return { x: OX + p.x * CELL, y: OY + p.y * CELL };
  }

  function drawBuilding(b, t) {
    const { gx, gy, h } = b;
    const s  = toScreen(gx,   gy);
    const sr = toScreen(gx+1, gy);
    const sf = toScreen(gx,   gy+1);
    const sb = toScreen(gx+1, gy+1);
    const uh = h * CELL * ISO_SY * 1.15;
    const pulse = 0.7 + 0.3 * Math.sin(t * 0.0008 + b.pulse);

    // Linke Wand
    ctx.beginPath();
    ctx.moveTo(s.x,  s.y);
    ctx.lineTo(sf.x, sf.y);
    ctx.lineTo(sf.x, sf.y - uh);
    ctx.lineTo(s.x,  s.y  - uh);
    ctx.closePath();
    ctx.fillStyle = C.buildFill;
    ctx.fill();
    ctx.strokeStyle = C.buildEdge;
    ctx.lineWidth = 0.7;
    ctx.globalAlpha = pulse * 0.85;
    ctx.stroke();

    // Rechte Wand
    ctx.beginPath();
    ctx.moveTo(s.x,  s.y);
    ctx.lineTo(sr.x, sr.y);
    ctx.lineTo(sr.x, sr.y - uh);
    ctx.lineTo(s.x,  s.y  - uh);
    ctx.closePath();
    ctx.fillStyle = C.buildFill;
    ctx.fill();
    ctx.strokeStyle = C.buildEdge;
    ctx.lineWidth = 0.7;
    ctx.stroke();

    // Dach
    ctx.beginPath();
    ctx.moveTo(s.x,  s.y  - uh);
    ctx.lineTo(sr.x, sr.y - uh);
    ctx.lineTo(sb.x, sb.y - uh);
    ctx.lineTo(sf.x, sf.y - uh);
    ctx.closePath();
    ctx.fillStyle = C.buildTop;
    ctx.fill();
    ctx.strokeStyle = C.buildEdge;
    ctx.lineWidth = 0.9;
    ctx.globalAlpha = pulse;
    ctx.stroke();

    // Dach-Glow für hohes Gebäude
    if (h >= 6) {
      ctx.beginPath();
      ctx.moveTo(s.x,  s.y  - uh);
      ctx.lineTo(sr.x, sr.y - uh);
      ctx.lineTo(sb.x, sb.y - uh);
      ctx.lineTo(sf.x, sf.y - uh);
      ctx.closePath();
      ctx.strokeStyle = C.dataBlue;
      ctx.lineWidth = 1.5;
      ctx.globalAlpha = 0.35 * pulse;
      ctx.stroke();
    }

    // Fenster (linke Wand)
    ctx.globalAlpha = 0.45 * pulse;
    const wh = 4, ww = 5;
    for (let row = 0; row < b.winRows; row++) {
      for (let col = 0; col < b.winCols; col++) {
        const wx = s.x + (col - 0.5) * 6 - 2;
        const baseY = s.y - uh + 6;
        const wy = baseY + row * (CELL * ISO_SY * 0.9 + 2);
        ctx.fillStyle = C.buildWin;
        ctx.fillRect(wx, wy, ww, wh);
      }
    }
    ctx.globalAlpha = 1;
  }

  // ─── Iso-Gitter ────────────────────────────────────────────────────────────

  function drawGrid(t) {
    ctx.globalAlpha = 1;
    for (let i = 0; i <= GRID; i++) {
      // X-Linien
      const a = toScreen(i, 0);
      const b = toScreen(i, GRID);
      const grad = ctx.createLinearGradient(a.x, a.y, b.x, b.y);
      grad.addColorStop(0,   'rgba(37,99,235,0.0)');
      grad.addColorStop(0.5, C.gridLine);
      grad.addColorStop(1,   'rgba(37,99,235,0.0)');
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.strokeStyle = grad;
      ctx.lineWidth = 0.5;
      ctx.stroke();
      // Y-Linien
      const c = toScreen(0, i);
      const d = toScreen(GRID, i);
      ctx.beginPath();
      ctx.moveTo(c.x, c.y);
      ctx.lineTo(d.x, d.y);
      ctx.stroke();
    }
    // Kreuzungspunkte — gelegentlich aufleuchten
    for (let gx = 0; gx <= GRID; gx += 2) {
      for (let gy = 0; gy <= GRID; gy += 2) {
        const p = toScreen(gx, gy);
        const blink = 0.5 + 0.5 * Math.sin(t * 0.0015 + gx * 0.7 + gy * 1.1);
        ctx.globalAlpha = 0.12 + 0.35 * blink;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
        ctx.fillStyle = C.dataBlue;
        ctx.fill();
      }
    }
    ctx.globalAlpha = 1;
  }

  // ─── Datenstrompulse ────────────────────────────────────────────────────────

  function drawConnections(t) {
    connections.forEach(cn => {
      cn.progress += cn.speed;
      if (cn.progress > 1) cn.progress = 0;

      const a = toScreen(cn.ax, cn.ay);
      const b = toScreen(cn.bx, cn.by);

      // Linie
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.strokeStyle = cn.color;
      ctx.lineWidth = 0.8;
      ctx.globalAlpha = 0.18;
      ctx.stroke();

      // Puls-Dot
      const px = a.x + (b.x - a.x) * cn.progress;
      const py = a.y + (b.y - a.y) * cn.progress;
      ctx.globalAlpha = 0.9;
      ctx.beginPath();
      ctx.arc(px, py, 3, 0, Math.PI * 2);
      ctx.fillStyle = cn.color;
      ctx.fill();

      // Dot-Glow
      ctx.globalAlpha = 0.25;
      ctx.beginPath();
      ctx.arc(px, py, 7, 0, Math.PI * 2);
      ctx.fillStyle = cn.color;
      ctx.fill();

      ctx.globalAlpha = 1;
    });
  }

  // ─── Alpine Silhouette ─────────────────────────────────────────────────────

  function drawAlpineSilhouette() {
    // Vereinfachte Bergsilhouette im Hintergrund
    const pts = [
      [0, H],
      [0, H * 0.72],
      [W * 0.04, H * 0.68],
      [W * 0.08, H * 0.58],
      [W * 0.13, H * 0.65],
      [W * 0.17, H * 0.42],   // Hochspitze 1
      [W * 0.21, H * 0.55],
      [W * 0.26, H * 0.48],
      [W * 0.30, H * 0.38],   // Hochspitze 2
      [W * 0.34, H * 0.52],
      [W * 0.38, H * 0.46],
      [W * 0.43, H * 0.60],
      [W * 0.50, H * 0.72],   // Tal
      [W * 0.55, H * 0.62],
      [W * 0.60, H * 0.44],   // Hochspitze 3
      [W * 0.65, H * 0.57],
      [W * 0.70, H * 0.50],
      [W * 0.75, H * 0.63],
      [W * 0.80, H * 0.55],
      [W * 0.85, H * 0.40],   // Hochspitze 4
      [W * 0.89, H * 0.52],
      [W * 0.93, H * 0.62],
      [W * 0.96, H * 0.68],
      [W, H * 0.72],
      [W, H],
    ];

    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    pts.forEach(([px, py]) => ctx.lineTo(px, py));
    ctx.closePath();
    ctx.fillStyle = C.alpine;
    ctx.fill();

    // Bergkanten leuchten
    ctx.beginPath();
    ctx.moveTo(pts[1][0], pts[1][1]);
    for (let i = 2; i < pts.length - 2; i++) {
      ctx.lineTo(pts[i][0], pts[i][1]);
    }
    ctx.strokeStyle = C.alpineEdge;
    ctx.lineWidth = 1.2;
    ctx.globalAlpha = 0.6;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  // ─── ORION-Signet ──────────────────────────────────────────────────────────
  // Das Symbol ⊘∞⧈∞⊘ als geometrische Komposition

  function drawSignet(t) {
    signetAngle = t * 0.00025;
    const cx = W * 0.87;
    const cy = H * 0.22;
    const R  = Math.min(W, H) * 0.072;

    ctx.save();
    ctx.translate(cx, cy);

    // Äußerer Glüh-Ring
    const glow = ctx.createRadialGradient(0, 0, R * 0.3, 0, 0, R * 1.5);
    glow.addColorStop(0,   'rgba(37,99,235,0.15)');
    glow.addColorStop(0.5, 'rgba(37,99,235,0.06)');
    glow.addColorStop(1,   'rgba(37,99,235,0.0)');
    ctx.beginPath();
    ctx.arc(0, 0, R * 1.5, 0, Math.PI * 2);
    ctx.fillStyle = glow;
    ctx.fill();

    // Doppelter Kreis ⊘
    ctx.beginPath();
    ctx.arc(0, 0, R, 0, Math.PI * 2);
    ctx.strokeStyle = C.signetGlow;
    ctx.lineWidth = 1.2;
    ctx.globalAlpha = 0.7;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, R * 0.7, 0, Math.PI * 2);
    ctx.stroke();

    // Diagonale im Kreis
    ctx.rotate(signetAngle);
    ctx.beginPath();
    ctx.moveTo(-R * 0.95,  R * 0.95);
    ctx.lineTo( R * 0.95, -R * 0.95);
    ctx.strokeStyle = C.signetGlow;
    ctx.lineWidth = 1.0;
    ctx.stroke();

    // Quadrat ⧈
    ctx.rotate(signetAngle * 0.5);
    const sq = R * 0.55;
    ctx.beginPath();
    ctx.rect(-sq, -sq, sq * 2, sq * 2);
    ctx.strokeStyle = C.dataBlue;
    ctx.lineWidth = 0.9;
    ctx.globalAlpha = 0.55;
    ctx.stroke();

    // Innenpunkte
    ctx.rotate(signetAngle * 1.5);
    for (let i = 0; i < 8; i++) {
      const a  = (Math.PI * 2 * i) / 8;
      const pr = R * 0.45;
      const blink = 0.4 + 0.6 * Math.sin(t * 0.001 + i * 0.8);
      ctx.beginPath();
      ctx.arc(Math.cos(a) * pr, Math.sin(a) * pr, 2, 0, Math.PI * 2);
      ctx.fillStyle = C.dataBlue;
      ctx.globalAlpha = blink * 0.8;
      ctx.fill();
    }

    // Mittelpunkt
    ctx.globalAlpha = 0.9;
    ctx.beginPath();
    ctx.arc(0, 0, 3, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    // ORION Text
    ctx.globalAlpha = 0.7;
    ctx.font = `bold ${R * 0.28}px 'Segoe UI', sans-serif`;
    ctx.fillStyle = C.dataBlue;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('ORION', 0, R * 1.35);

    ctx.restore();
    ctx.globalAlpha = 1;
  }

  // ─── Partikel ──────────────────────────────────────────────────────────────

  function spawnParticles(t) {
    if (particles.length < 60 && Math.random() < 0.25) {
      const gx = Math.random() * GRID;
      const gy = Math.random() * GRID;
      const sp = toScreen(gx, gy);
      const colors = [C.dataBlue, C.dataGreen, C.dataPurple, C.dataOrange];
      particles.push({
        x: sp.x, y: sp.y,
        vx: (Math.random() - 0.5) * 0.6,
        vy: -0.4 - Math.random() * 0.8,
        life: 0,
        maxLife: 80 + Math.random() * 120,
        r: 1.2 + Math.random() * 1.5,
        color: colors[Math.floor(Math.random() * colors.length)],
      });
    }
  }

  function drawParticles() {
    particles.forEach((p, i) => {
      p.x  += p.vx;
      p.y  += p.vy;
      p.vy *= 0.995;
      p.life++;
      const alpha = 1 - p.life / p.maxLife;
      ctx.globalAlpha = alpha * 0.75;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();
    });
    particles = particles.filter(p => p.life < p.maxLife);
    ctx.globalAlpha = 1;
  }

  // ─── Scanlines ─────────────────────────────────────────────────────────────

  function drawScanlines() {
    ctx.globalAlpha = 1;
    for (let y = 0; y < H; y += 3) {
      ctx.fillStyle = C.scanline;
      ctx.fillRect(0, y, W, 1);
    }
  }

  // ─── Vignette ──────────────────────────────────────────────────────────────

  function drawVignette() {
    const vg = ctx.createRadialGradient(W/2, H/2, H * 0.2, W/2, H/2, H * 0.85);
    vg.addColorStop(0,   'rgba(0,0,0,0)');
    vg.addColorStop(0.7, 'rgba(0,0,0,0.15)');
    vg.addColorStop(1,   'rgba(0,0,0,0.55)');
    ctx.fillStyle = vg;
    ctx.fillRect(0, 0, W, H);
  }

  // ─── Koordinaten-Overlay ────────────────────────────────────────────────────

  function drawOverlay(t) {
    const alpha = 0.35 + 0.15 * Math.sin(t * 0.0005);
    ctx.globalAlpha = alpha;
    ctx.font = '8px "Courier New", monospace';
    ctx.fillStyle = C.dataBlue;
    ctx.textAlign = 'left';

    const lines = [
      `ORION Architekt-AT  v3.0`,
      `AT-GRID  ${GRID}×${GRID}  AKTIV`,
      `BIM/IFC  ● ONLINE`,
      `OIB-RL6:2023  ● SYNC`,
      `KI-MODELL  ● GELADEN`,
      `PARTIKEL  ${particles.length.toString().padStart(3,' ')}`,
    ];
    lines.forEach((line, i) => {
      ctx.fillText(line, 10, 18 + i * 12);
    });

    ctx.globalAlpha = 1;
  }

  // ─── Haupt-Render-Loop ─────────────────────────────────────────────────────

  let raf;
  function render(t) {
    ctx.fillStyle = C.bg;
    ctx.fillRect(0, 0, W, H);

    drawAlpineSilhouette();
    drawGrid(t);

    // Gebäude von hinten nach vorne (Painter's algorithm)
    const sorted = [...buildings].sort((a, b) => (a.gx + a.gy) - (b.gx + b.gy));
    sorted.forEach(b => drawBuilding(b, t));

    drawConnections(t);
    spawnParticles(t);
    drawParticles();
    drawSignet(t);
    drawScanlines();
    drawVignette();
    drawOverlay(t);

    raf = requestAnimationFrame(render);
  }

  // ─── Interaktion: Hover-Glow auf Gebäude ───────────────────────────────────

  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    buildings.forEach(b => {
      const s = toScreen(b.gx + 0.5, b.gy + 0.5);
      const dist = Math.hypot(mx - s.x, my - s.y);
      if (dist < 30) {
        b.pulse = Date.now() * 0.003;  // beschleunigt Puls bei Hover
      }
    });
  });

  // ─── Start ─────────────────────────────────────────────────────────────────

  initScene();
  raf = requestAnimationFrame(render);

  // Aufräumen wenn Canvas aus DOM verschwindet
  const observer = new MutationObserver(() => {
    if (!document.contains(canvas)) {
      cancelAnimationFrame(raf);
      observer.disconnect();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });

})();
