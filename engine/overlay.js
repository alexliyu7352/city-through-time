// 2D layer over the model (adapted from lemo-opuscar's white-model demo, MIT): readouts in the left third, pins anchored
// to the model through the camera, marks, the subtitle strip, the identity label and the end card.
// Every text that must be read registers in TX for readcheck.
import { clamp, lerp, seg, ss, eo } from './lib.js';

export const W = 1920, H = 1080;
// the project's credit: the end card draws it on every film, the player links it (LICENSE, condition 2)
export const CREDIT = '一城春秋 · A City Through Time  ·  github.com/alexliyu7352/city-through-time', REPO = 'https://github.com/alexliyu7352/city-through-time';
// the film's type, one font per job (city.yaml film.fonts, resolved by compile into FILM.fonts.roles: 'weight {}px alias')
let F = {};
export function setFonts(roles) { F = roles; }
// the film's languages (compile: FILM.ui from i18n/<code>.yaml): the words the program writes itself, and the subtitle lines' type
let UI = { chapter: 'CHAPTER {n}', locator: 'LOCATOR' };
export function setUI(ui, sub) { if (ui) UI = { ...UI, ...ui }; if (sub) { SUB.a = sub.a; SUB.b = sub.b; } }
const plain = s => !/[^\x00-\x7f]/.test(s);   // (an ASCII word may take the mono face; any other script takes the first language's)
export const font = (k, px) => { if (!F[k]) throw new Error(`no font for the job ${k} (film.fonts)`); return F[k].replace('{}', px); };
export const SUB = { a: ['zh_strong', 38], b: ['en', 30], safe: 1500 };
const SUBTOP = H - 145;   // the subtitle strip starts here: pins and labels keep out of it

// size: the layer's size in its own pixels, the film's 1920 x 1080 picture unless a page that fills its window (engine/view.js's
// public mode) draws its pins on a layer of the window's size
export function makeOverlay(canvas, size = { w: W, h: H }) {
  const g = canvas.getContext('2d'), LW = size.w, LH = size.h, LSUB = LH - 145;   // (LSUB: SUBTOP on this layer)
  let TX = [], DRAWN = [];   // DRAWN: every text drawn opaque, named or not, its letters' band (tools/readcheck.mjs: texts over texts)
  const begin = () => { g.clearRect(0, 0, LW, LH); TX = []; DRAWN = []; };
  function txt(id, s, x, y, k, px, col, a = 1, o = {}) {
    if (a <= .001 || !s) return 0;
    g.save(); g.globalAlpha = a; g.font = font(k, px); g.fillStyle = col; g.textBaseline = 'alphabetic';
    if (o.ls) g.letterSpacing = o.ls + 'px';
    if (o.shadow) { g.shadowColor = 'rgba(0,0,0,.6)'; g.shadowBlur = o.shadow; }
    const w = g.measureText(s).width, xx = o.right ? x - w : o.center ? x - w / 2 : x;
    g.fillText(s, xx, y); g.restore();
    if (id && a > .98) TX.push({ id, text: s, x0: xx, y0: y - px * .9, x1: xx + w, y1: y + px * .25 });
    if (a > .98) DRAWN.push({ id: id || null, text: s, x0: xx, y0: y - px * .7, x1: xx + w, y1: y });
    return w;
  }
  const width = (s, k, px, ls = 0) => { g.save(); g.font = font(k, px); g.letterSpacing = ls + 'px'; const w = g.measureText(s).width; g.restore(); return w; };
  const env = (t, t0, t1, fin = .35, fout = .3) => Math.min(eo(seg(t, t0, t0 + fin)), 1 - ss(seg(t, t1 - fout, t1)));

  function scrims(a, sub) {
    if (a > 0) {
      const gr = g.createRadialGradient(300, 600, 40, 300, 600, 640);
      gr.addColorStop(0, `rgba(4,5,8,${.6 * a})`); gr.addColorStop(.55, `rgba(4,5,8,${.36 * a})`); gr.addColorStop(1, 'rgba(4,5,8,0)');
      g.fillStyle = gr; g.fillRect(0, 0, W, H);
    }
    if (sub > 0) {
      const g3 = g.createLinearGradient(0, H, 0, H - 210); g3.addColorStop(0, `rgba(4,5,8,${.62 * sub})`); g3.addColorStop(1, 'rgba(4,5,8,0)');
      g.fillStyle = g3; g.fillRect(0, H - 210, W, 210);
    }
  }

  // a readout's source note in lines that stay on the dark ground on the left: broken at its separators (a · with a space after
  // it, not the one inside 《史记·秦始皇本纪》) to at most NOTE_W px a line (one source wider than that stays whole); noteDrop: how
  // far its extra lines push what is below it down
  const NOTE_W = 620, NOTE_LH = 22;
  function noteLines(s) {
    if (!s) return [];
    const tk = s.split(/(\s*·\s+)/), out = []; let cur = tk[0];   // [source, separator, source, ...]
    for (let i = 1; i < tk.length; i += 2) {
      const nx = cur + tk[i] + tk[i + 1];
      if (width(nx, 'mono', 16, 1) > NOTE_W) { out.push(cur); cur = tk[i + 1]; } else cur = nx;
    }
    return [...out, cur];
  }
  const noteDrop = s => Math.max(0, noteLines(s).length - 1) * NOTE_LH;

  // readout: index + layer name, one figure (+unit), one label, one source line, legend rows [{col, text, text2}]
  function readout(t, o) {
    const a = env(t, o.t0, o.t1); if (a <= 0) return;
    const k = eo(seg(t, o.t0, o.t0 + .6)), dy = (1 - k) * 26, X = 96, Y = 568 + dy;
    // chapter line: index · name, a hairline in the era's colour
    const ch = UI.chapter.replace('{n}', o.idx); txt(o.id + 'i', ch, X, Y - 150, plain(ch) ? 'mono' : 'zh', 15, 'rgba(235,238,242,.7)', a, { ls: 4, shadow: 6 });
    txt(o.id + 'n', o.name, X, Y - 112, 'zh_strong', 30, '#f4f1ea', a, { ls: 6, shadow: 8 });
    g.save(); g.globalAlpha = a; g.fillStyle = o.col; g.fillRect(X, Y - 92, 220 * k, 1.5); g.restore();
    const bigId = o.live ? null : o.id + 'b';
    const big = String(o.big), sp = big.match(/^(\D*?)\s*(\d[\d,.]*)\s*(\D*)$/), cjk = sp && !plain(sp[1] + sp[3]);
    const px = o.bigPx || (big.length > 7 ? 104 : 150);
    // the year: a thin serif numeral; words around it in another script (前, 紀元前…年, 기원전…년) in the first language's face, smaller
    let w = 0;
    if (cjk) { const m = sp; if (m[1]) w = txt(bigId, m[1], X, Y + 6, 'zh', px * .5, '#f4f1ea', a, { shadow: 12 }) + 14; w += txt(bigId ? o.id + 'b2' : null, m[2], X + w, Y + 6, 'numeral', px, '#ffffff', a, { shadow: 16 });
      if (m[3]) w += 10 + txt(bigId ? o.id + 'b3' : null, m[3], X + w + 10, Y + 6, 'zh', px * .5, '#f4f1ea', a, { shadow: 12 }); }
    else w = txt(bigId, big, X - 4, Y + 6, 'numeral', px, '#ffffff', a, { shadow: 16 });
    if (o.unit) txt(bigId ? o.id + 'u' : null, o.unit, X + w + 10, Y + 4, 'zh', 44, 'rgba(244,241,234,.9)', a, { shadow: 10 });
    if (o.label) txt(o.id + 'l', o.label, X, Y + 58, 'zh', 30, '#f4f1ea', a, { shadow: 10, ls: 1 });
    // the source note: bright enough and shadowed to read over a lit map or the satellite plate, in lines;
    // readcheck reads it as one text, the whole note (it sets how short the stop may be: docs/STAGING.md 5d)
    const nl = noteLines(o.note), dn = noteDrop(o.note);
    nl.forEach((q, i) => txt(null, q, X, Y + 94 + i * NOTE_LH, 'mono', 16, 'rgba(225,230,236,.85)', a, { ls: 1, shadow: 8 }));
    if (nl.length && a > .98) TX.push({ id: o.id + 's', text: o.note, x0: X, y0: Y + 94 - 16 * .9, x1: X + Math.max(...nl.map(q => width(q, 'mono', 16, 1))), y1: Y + 94 + dn + 16 * .25 });
    if (o.legend) o.legend.forEach((row, i) => {
      const ra = a * (row.t0 != null ? seg(t, row.t0, row.t0 + .25) : 1); if (ra <= 0) return;
      const yy = Y + 128 + dn + i * 32;
      if (row.col) { g.save(); g.globalAlpha = ra; g.fillStyle = row.col; g.fillRect(X, yy - 12, 28, 14); g.restore(); }
      const w1 = row.text ? txt(o.id + 'g' + i, row.text, X + (row.col ? 44 : 0), yy, 'mono', 17, 'rgba(235,238,242,.85)', ra, { shadow: 6 }) : 0;
      if (row.text2) txt(o.id + 'h' + i, row.text2, X + Math.max(210, (row.col ? 44 : 0) + w1 + 18), yy, 'mono', 17, 'rgba(235,238,242,.85)', ra, { shadow: 6 });   // (after a long first name, not over it)
    });
    if (o.bar) {   // a gradient bar with end labels
      const gr = g.createLinearGradient(X, 0, X + 300, 0); o.bar.cols.forEach((c, i) => gr.addColorStop(i / (o.bar.cols.length - 1), c));
      g.save(); g.globalAlpha = a; g.fillStyle = gr; g.fillRect(X, Y + 128 + dn, 300, 4); g.restore();
      txt(null, o.bar.l0, X, Y + 158 + dn, 'mono', 17, 'rgba(230,234,240,.7)', a, { shadow: 6 });
      txt(null, o.bar.l1, X + 300, Y + 158 + dn, 'mono', 17, 'rgba(230,234,240,.7)', a, { right: true, shadow: 6 });
    }
  }

  // a tag on the model, one look for every label on the map (pins and place names): a dot, a pole straight up that becomes
  // the edge of a small dark box with the name (and a second line). The pole's length and the side of the box are laid out
  // by compile (pipeline/tags.py: tags clear of each other and of the subtitles, readout and locator). a: alpha; grow: 0..1
  // how far the pole has drawn. Returns where its box is drawn ({ x, y, w, h }: a page that makes it a link puts the link there)
  const TAG = { a: ['zh_strong', 20], b: ['en_strong', 14], pad: 11, top: 128 };
  function tag(x, y, o, a, grow = 1) {
    const boxH = o.sub ? 50 : 32, col = o.col || '#ffffff';
    let L = (o.len || 160), yTop = y - L - boxH;
    yTop = Math.min(yTop, LSUB - 14 - boxH); yTop = Math.max(yTop, TAG.top); L = y - yTop - boxH; if (L < 24) return;   // clear of the subtitles and the timeline
    const ta = a * (o.ta ?? 1);
    let w = width(o.text, TAG.a[0], TAG.a[1], 1); if (o.sub) w = Math.max(w, width(o.sub, TAG.b[0], TAG.b[1], .3)); w += 2 * TAG.pad;
    const left = o.left != null ? !!o.left : x + w > LW - 40;
    const yPole = y - (y - yTop) * grow;
    g.save(); g.globalAlpha = a * .35; g.fillStyle = col; g.beginPath(); g.arc(x, y, 7, 0, 7); g.fill(); g.restore();   // the dot, with a halo
    g.save(); g.globalAlpha = a;
    g.strokeStyle = 'rgba(0,0,0,.35)'; g.lineWidth = 3.5; g.beginPath(); g.moveTo(x, y); g.lineTo(x, yPole); g.stroke();
    g.strokeStyle = col; g.lineWidth = 1.4; g.beginPath(); g.moveTo(x, y); g.lineTo(x, yPole); g.stroke();
    g.fillStyle = col; g.beginPath(); g.arc(x, y, 3.2, 0, 7); g.fill();
    g.restore();
    if (ta <= 0) return;
    const bx = left ? x - w : x;
    g.save(); g.globalAlpha = ta * .6; g.fillStyle = '#07080c'; g.fillRect(bx, yTop, w, boxH); g.restore();
    g.save(); g.globalAlpha = ta; g.fillStyle = col; g.fillRect(left ? x - 1 : x - 1, yTop, 2, boxH); g.restore();   // the pole as the box's edge
    const tx_ = left ? x - TAG.pad : x + TAG.pad;
    txt(o.id, o.text, tx_, yTop + 23, TAG.a[0], TAG.a[1], '#ffffff', ta, { shadow: 8, right: left, ls: 1 });
    if (o.sub) txt(o.id ? o.id + 's' : null, o.sub, tx_, yTop + 42, TAG.b[0], TAG.b[1], 'rgba(240,242,245,.85)', ta, { shadow: 6, right: left, ls: .3 });
    return { x: bx, y: yTop, w, h: boxH };
  }
  function pin(t, p, o, k = 1) {
    if (!p) return;
    const edge = ss(seg(Math.min(p[0], LW - p[0]), 0, 90)) * ss(seg(p[1], 20, 110));   // its building leaving the frame: the pin goes with it
    const a = env(t, o.t0, o.t1, .3, .3) * (1 - ss(seg(p[1], LSUB - 10, LSUB + 50))) * edge * k; if (a <= 0) return;   // an anchor down in the subtitles: no pin
    return tag(p[0], p[1], { ...o, ta: seg(t, o.t0 + .15, o.t0 + .4) }, a, eo(seg(t, o.t0, o.t0 + .45)));
  }


  // mark: a ring that pops on a point of the model
  function mark(t, p, o) {
    const a = Math.min(seg(t, o.t0, o.t0 + .15), 1 - ss(seg(t, o.t1 - .4, o.t1))); if (a <= 0 || !p) return;
    const pop = 1 + 1.2 * Math.exp(-(t - o.t0) / .12), col = o.col || '#ffffff', r = o.r || 10;
    g.save(); g.globalAlpha = a; g.strokeStyle = col; g.lineWidth = 2.4; g.beginPath(); g.arc(p[0], p[1], r * pop, 0, 7); g.stroke();
    g.fillStyle = col; g.beginPath(); g.arc(p[0], p[1], 2.5, 0, 7); g.fill(); g.restore();
  }

  // a measured line on the model: grows from A to B with ticks, reading at the tip
  function rangeLine(t, t0, t1, tOut, pts, o) {
    const a = 1 - ss(seg(t, tOut - .3, tOut)); if (t < t0 || a <= 0) return;
    const k = eo(seg(t, t0, t1));
    const n = pts.length - 1, m = Math.max(1, Math.round(n * k));
    g.save(); g.globalAlpha = a; g.lineCap = 'round';
    g.strokeStyle = 'rgba(0,0,0,.45)'; g.lineWidth = 6; g.beginPath(); pts.slice(0, m + 1).forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke();
    g.strokeStyle = o.col; g.lineWidth = 2.4; g.beginPath(); pts.slice(0, m + 1).forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke();
    for (const i of (o.ticks || [])) if (i <= m) { const [x, y] = pts[i]; g.fillStyle = o.col; g.beginPath(); g.arc(x, y, 3, 0, 7); g.fill(); }
    const [tx, ty] = pts[m]; g.fillStyle = '#fff'; g.beginPath(); g.arc(tx, ty, 5, 0, 7); g.fill();
    g.restore();
    return pts[m];
  }

  // subtitle strip: primary line above, secondary below (if any), single lines centred at the bottom
  function subtitle(t, cue) {
    if (!cue) return;
    const a = Math.min(seg(t, cue.t0, cue.t0 + .12), 1 - seg(t, cue.t1 - .12, cue.t1)); if (a <= 0) return;
    if (cue.b) {
      txt(null, cue.a, W / 2, H - 96, ...SUB.a, '#ffffff', a, { center: true, shadow: 14, ls: 1.5 });
      txt(null, cue.b, W / 2, H - 50, ...SUB.b, 'rgba(236,240,244,.88)', a, { center: true, shadow: 10, ls: .6 });
    } else txt(null, cue.a, W / 2, H - 62, ...SUB.a, '#ffffff', a, { center: true, shadow: 14, ls: 1.5 });
  }

  // timeline bar, top centre: film time on the x axis, a tick per node (labelled with its first year), a cursor with the current year
  function timelineBar(t, bar, yearText, label, a = 1) {
    if (a <= 0) return;
    const X0 = 1040, X1 = 1824, Y = 66;
    const k = clamp((t - bar.from) / Math.max(1e-6, bar.to - bar.from), 0, 1);
    g.save(); g.globalAlpha = a;
    g.strokeStyle = 'rgba(235,238,242,.28)'; g.lineWidth = 1; g.beginPath(); g.moveTo(X0, Y); g.lineTo(X1, Y); g.stroke();
    g.strokeStyle = 'rgba(255,255,255,.9)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(X0, Y); g.lineTo(X0 + (X1 - X0) * k, Y); g.stroke();
    g.fillStyle = 'rgba(235,238,242,.55)';
    let lastX = -999;
    for (const tk of bar.ticks) {
      const x = X0 + (X1 - X0) * clamp((tk.t - bar.from) / (bar.to - bar.from), 0, 1);
      g.fillRect(x - .5, Y - 5, 1, 10);
      if (x - lastX > 58) { txt(null, tk.yearLabel, x, Y + 24, 'mono', 13, 'rgba(225,230,236,.5)', a, { center: true }); lastX = x; }
    }
    const cx = X0 + (X1 - X0) * k;
    g.fillStyle = '#ffffff'; g.beginPath(); g.arc(cx, Y, 3.2, 0, 7); g.fill();
    g.restore();
    txt(null, yearText, cx, Y - 16, 'numeral_strong', 26, '#ffffff', a, { center: true, shadow: 8 });
    if (label) txt(null, label, X0 - 28, Y + 6, 'zh', 17, 'rgba(230,234,240,.78)', a, { right: true, ls: 2 });
  }

  // terrain section: a profile of the ground along a line, with labelled steps (metres), drawn as a small instrument panel
  function section(t, sec, a) {
    if (a <= 0) return;
    const X0 = 1240, Y0 = 760, Wd = 580, Hd = 150; const k = eo(seg(t, sec.t0, sec.t0 + 1.2));
    g.save(); g.globalAlpha = a;
    g.fillStyle = 'rgba(5,6,10,.5)'; g.fillRect(X0 - 24, Y0 - 150, Wd + 48, Hd + 110);
    const n = sec.profile.length, lo = sec.lo, hi = sec.hi;
    const px = i => X0 + Wd * i / (n - 1), py = h => Y0 - (h - lo) / (hi - lo) * Hd;
    g.beginPath(); g.moveTo(px(0), Y0 + 2);
    for (let i = 0; i < Math.max(2, Math.round(n * k)); i++) g.lineTo(px(i), py(sec.profile[i]));
    const last = Math.max(1, Math.round(n * k) - 1); g.lineTo(px(last), Y0 + 2); g.closePath();
    g.fillStyle = 'rgba(255,225,170,.14)'; g.fill();
    g.strokeStyle = '#ffe3b0'; g.lineWidth = 1.6; g.beginPath();
    for (let i = 0; i < Math.max(2, Math.round(n * k)); i++) i ? g.lineTo(px(i), py(sec.profile[i])) : g.moveTo(px(i), py(sec.profile[i]));
    g.stroke();
    g.strokeStyle = 'rgba(235,238,242,.25)'; g.lineWidth = 1; g.beginPath(); g.moveTo(X0, Y0 + 2); g.lineTo(X0 + Wd, Y0 + 2); g.stroke();
    g.restore();
    txt(null, sec.title, X0, Y0 - 118, 'zh_strong', 20, '#f4f1ea', a, { ls: 3 });
    txt(null, sec.sub, X0, Y0 - 92, 'mono', 13, 'rgba(225,230,236,.6)', a, { ls: 1 });
    for (const L of sec.labels) {   // {k: 0..1 along the line, text, h}
      const i = Math.round(L.k * (n - 1)); if (i > n * k) continue;
      const x = px(i), y = py(sec.profile[i]);
      g.save(); g.globalAlpha = a; g.fillStyle = '#ffe3b0'; g.beginPath(); g.arc(x, y, 3, 0, 7); g.fill(); g.restore();
      txt(null, L.text, x, y - 14, 'zh', 16, '#ffffff', a, { center: true, shadow: 6 });
      txt(null, `${Math.round(sec.profile[i])} m`, x, y + 24, 'numeral_strong', 17, 'rgba(255,227,176,.95)', a, { center: true });
    }
    txt(null, sec.l0, X0, Y0 + 44, 'mono', 13, 'rgba(225,230,236,.6)', a); txt(null, sec.l1, X0 + Wd, Y0 + 44, 'mono', 13, 'rgba(225,230,236,.6)', a, { right: true });
  }

  // a real clip inside the frame: letterboxed with a thin rule and a credit line
  // today's echo: the real place. Modes —
  //   full : a 4K clip or photo over the whole frame, revealed by a sweeping light edge, slow push-in, caption lower left
  //   panel: a photo sliding in over the right 62 % of the frame, its left edge melting into the map (the map stays live)
  //   card : a small floating card (low-resolution sources) tied to its place on the map by a leader line
  //   doc  : a historical map or drawing as a document card (never draped over the terrain)
  // e = { in: 0..1, out: 0..1, k: 0..1 over the clip }, anchor = [x, y] on screen (card mode)
  let OFF = null;
  const offscreen = () => { if (!OFF) { OFF = document.createElement('canvas'); OFF.width = W; OFF.height = H; } const o = OFF.getContext('2d'); o.clearRect(0, 0, W, H); return [OFF, o]; };
  function cover(gg, src, x, y, w, h, z, panX = 0, panY = 0) {
    const isVid = src instanceof HTMLVideoElement, sw = isVid ? src.videoWidth : src.naturalWidth, sh = isVid ? src.videoHeight : src.naturalHeight;
    if (!sw) return; const s0 = Math.max(w / sw, h / sh) * z, dw = sw * s0, dh = sh * s0;
    gg.drawImage(src, x + (w - dw) / 2 + panX * (dw - w) / 2, y + (h - dh) / 2 + panY * (dh - h) / 2, dw, dh);
  }
  function caption(f, x, y, a, o = {}) {
    if (a <= 0) return;
    txt(null, f.kicker || '今天 · TODAY · 实拍', x, y, 'mono', 14, 'rgba(240,242,245,.78)', a, { ls: 4, shadow: 8 });
    txt(null, f.title || '', x, y + 42, 'zh_strong', o.big ? 40 : 32, '#ffffff', a, { ls: 3, shadow: 14 });
    if (f.sub) txt(null, f.sub, x, y + (o.big ? 78 : 70), 'en', o.big ? 22 : 19, 'rgba(240,242,245,.88)', a, { shadow: 10 });
  }
  function footage(src, e, f, anchor) {
    if (!src || (e.in <= 0 && e.out <= 0)) return;
    const isVid = src instanceof HTMLVideoElement; if (isVid && src.readyState < 2) return;
    const mode = f.mode || 'full', vis = ss(e.in) * (1 - ss(e.out));
    if (vis <= 0) return;
    const ta = ss(seg(e.in, .55, 1)) * (1 - ss(seg(e.out, 0, .45)));
    if (mode === 'full') {
      const bar = 70, x0 = W * eo(e.in) * 0, xa = W * (1 - eo(e.in)), xb = W * eo(e.out);   // reveal from the left, leave to the right
      const L = Math.max(0, xb), R = W - Math.max(0, xa);
      g.save(); g.beginPath(); g.rect(L, 0, Math.max(0, R - L), H); g.clip();
      g.fillStyle = '#05060a'; g.fillRect(0, 0, W, H);
      g.beginPath(); g.rect(0, bar, W, H - 2 * bar); g.clip();
      cover(g, src, 0, bar, W, H - 2 * bar, 1.02 + .08 * e.k, (f.pan || 0) * (e.k * 2 - 1), 0);
      const vg = g.createLinearGradient(0, H - bar - 320, 0, H - bar); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.55)');
      g.fillStyle = vg; g.fillRect(0, H - bar - 320, W, 320);
      g.restore();
      for (const ex of [R, L]) if (ex > 2 && ex < W - 2) {   // the sweeping light edge
        const gl = g.createLinearGradient(ex - 40, 0, ex + 40, 0); gl.addColorStop(0, 'rgba(255,240,220,0)'); gl.addColorStop(.5, 'rgba(255,240,220,.85)'); gl.addColorStop(1, 'rgba(255,240,220,0)');
        g.fillStyle = gl; g.fillRect(ex - 40, 0, 80, H);
      }
      caption(f, 96, H - bar - 150, ta, { big: true });
      if (f.credit) txt(null, f.credit, W - 96, H - bar - 24, 'mono', 13, 'rgba(225,230,236,.72)', ta, { right: true, shadow: 8 });
      return;
    }
    if (mode === 'panel') {
      const px0 = W * .36, slide = (1 - eo(e.in)) * 140 + ss(e.out) * 80, pw = W - px0;
      const [oc, o] = offscreen();
      cover(o, src, px0 + slide, 0, pw, H, 1.03 + .06 * e.k, (f.pan || 0) * (e.k * 2 - 1), 0);
      o.globalCompositeOperation = 'destination-in';                       // melt the left edge into the map
      const m = o.createLinearGradient(px0 + slide, 0, px0 + slide + 260, 0); m.addColorStop(0, 'rgba(0,0,0,0)'); m.addColorStop(1, 'rgba(0,0,0,1)');
      o.fillStyle = m; o.fillRect(0, 0, W, H); o.globalCompositeOperation = 'source-over';
      const sh = o.createLinearGradient(0, H - 380, 0, H); sh.addColorStop(0, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(0,0,0,.6)');
      o.fillStyle = sh; o.fillRect(px0 + slide + 200, H - 380, pw, 380);
      g.save(); g.globalAlpha = vis; g.drawImage(oc, 0, 0); g.restore();
      caption(f, px0 + slide + 240, H - 330, ta);
      if (f.credit) txt(null, f.credit, px0 + slide + 240, H - 236, 'mono', 13, 'rgba(225,230,236,.75)', ta, { shadow: 8 });
      return;
    }
    // card and doc: a framed picture with a shadow
    const isDoc = mode === 'doc';
    const sw = isVid ? src.videoWidth : src.naturalWidth, shh = isVid ? src.videoHeight : src.naturalHeight, ar = sw / shh;
    // a document fills the band between the top furniture (150) and its caption, which ends 140 px under the picture, above the subtitles
    const DOC0 = 150, DOCH = SUBTOP - 160 - DOC0;
    const ch = isDoc ? Math.min(640, DOCH) : 330, cw = Math.min(isDoc ? 820 : 600, ch * ar), chh = cw / ar;
    const cx = f.side === 'left' ? 120 : W - 120 - cw, cy = isDoc ? DOC0 + (DOCH - chh) / 2 : 170;
    const lift = (1 - eo(e.in)) * 60 + ss(e.out) * 30;
    g.save(); g.globalAlpha = vis;
    if (anchor && !isDoc) {   // the leader line to the place
      g.strokeStyle = 'rgba(255,255,255,.7)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(anchor[0], anchor[1]);
      const ax = cx + (anchor[0] < cx ? 0 : cw), ay = cy + lift + chh / 2; g.lineTo(ax, ay); g.stroke();
      g.fillStyle = '#ffffff'; g.beginPath(); g.arc(anchor[0], anchor[1], 4, 0, 7); g.fill();
    }
    g.shadowColor = 'rgba(0,0,0,.55)'; g.shadowBlur = 40; g.shadowOffsetY = 14;
    g.fillStyle = isDoc ? '#e9e2d2' : '#0b0d12'; g.fillRect(cx - 8, cy + lift - 8, cw + 16, chh + 16);
    g.shadowColor = 'transparent';
    g.beginPath(); g.rect(cx, cy + lift, cw, chh); g.clip();
    cover(g, src, cx, cy + lift, cw, chh, 1.0 + .05 * e.k);
    g.restore();
    caption(f, cx, cy + lift + chh + 44, ta);
    if (f.credit) txt(null, f.credit, cx, cy + lift + chh + (f.sub ? 140 : 110), 'mono', 12, 'rgba(225,230,236,.72)', ta, { shadow: 8 });
  }

  // a route's label: a dark pill with a coloured rule, sitting just above the arc
  function routeLabel(p, a, aTxt, bTxt, col) {
    if (a <= 0 || !p) return;
    const w1 = width(aTxt, 'zh_strong', 22, 2), w2 = bTxt ? width(bTxt, 'en_strong', 14, 1) : 0, w = Math.max(w1, w2) + 36, h = bTxt ? 64 : 42;
    const x = p[0] - w / 2, y = Math.min(p[1] - h - 18, SUBTOP - h);
    g.save(); g.globalAlpha = a * .9; g.fillStyle = 'rgba(8,10,14,.78)'; g.fillRect(x, y, w, h); g.fillStyle = col; g.fillRect(x, y, 3, h);
    g.strokeStyle = col; g.globalAlpha = a * .7; g.beginPath(); g.moveTo(p[0], p[1] - 18); g.lineTo(p[0], p[1] - 4); g.stroke(); g.restore();
    txt(null, aTxt, x + 18, y + 30, 'zh_strong', 22, '#ffffff', a, { ls: 2 });
    if (bTxt) txt(null, bTxt, x + 18, y + 52, 'en_strong', 14, 'rgba(235,238,242,.85)', a, { ls: 1 });
  }

  // counters under the readout: what changed so far (e.g. new buildings), numbers rolling with the year
  function counters(t, C, vals, a, dy = 0) {   // dy: below a readout's legend or bar (they share the left column)
    if (a <= 0) return;
    const X = 96, Y = 724 + dy;
    g.save(); g.globalAlpha = a * .5; g.fillStyle = 'rgba(255,255,255,.35)'; g.fillRect(X, Y - 34, 240, 1); g.restore();
    vals.forEach((v, i) => {
      const x = X + i * 200;
      txt(null, Math.round(v).toLocaleString('en-US'), x, Y + 8, 'numeral', 40, '#ffffff', a, { shadow: 12 });
      const A = C.a || C.zh, B = C.a ? C.b : C.en; txt(null, B ? `${A[i]} · ${B[i]}` : A[i], x, Y + 36, 'zh', 15, 'rgba(240,242,245,.8)', a, { shadow: 8, ls: 1 });
    });
    txt(null, C.note, X, Y + 62, 'mono', 13, 'rgba(225,230,236,.8)', a, { ls: 1, shadow: 6 });
  }

  // the sky over a city laid out after it: a night scrim over the model, a sparse field of stars, then each asterism drawn on
  // its place in the city in turn (stars first, then the lines between them) with the pair of names; one pale colour, thin lines.
  // P(x, y, z) projects a model point to the screen. Returns the sky's alpha (main.js quiets the map furniture under it).
  const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  function sky(t, SK, P) {
    const a = env(t, SK.on, SK.off, 1.4, 1.4); if (a <= 0) return 0;
    const [cr, cg, cb] = [1, 3, 5].map(i => parseInt(SK.col.slice(i, i + 2), 16)), rgba = al => `rgba(${cr},${cg},${cb},${al})`;
    g.save(); g.globalAlpha = a * SK.scrim; g.fillStyle = '#03060d'; g.fillRect(0, 0, W, H); g.restore();
    g.save(); g.fillStyle = rgba(1);
    for (let i = 0; i < 240; i++) {   // the field: fixed on the screen, a slow twinkle
      const h3 = hash(i * 5.1 + .7); g.globalAlpha = a * (.12 + .3 * h3) * (.6 + .4 * Math.sin(t * 1.1 + i * 2.3));
      g.beginPath(); g.arc(hash(i * 1.37) * W, hash(i * 2.71 + .3) * H, .5 + h3 * h3 * 1.3, 0, 7); g.fill();
    }
    g.restore();
    const star = (p, m, al) => {
      const r = 5 + 7 * m, gr = g.createRadialGradient(p[0], p[1], 0, p[0], p[1], r * 2.6);
      gr.addColorStop(0, rgba(.9 * al)); gr.addColorStop(.22, rgba(.28 * al)); gr.addColorStop(1, rgba(0));
      g.fillStyle = gr; g.fillRect(p[0] - r * 2.6, p[1] - r * 2.6, r * 5.2, r * 5.2);
      g.fillStyle = `rgba(255,255,255,${al})`; g.beginPath(); g.arc(p[0], p[1], .9 + 1.1 * m, 0, 7); g.fill();
    };
    g.save(); g.globalCompositeOperation = 'lighter';
    for (const G of SK.groups) {
      const k = seg(t, G.on, G.on + G.draw); if (k <= 0) continue;
      if (G.band) {   // a river of stars flowing in along the line
        const line = G.band.line.filter(q => q[3] <= k).map(q => P(q[0], q[2], q[1])).filter(Boolean);
        if (line.length > 1) for (const [w, al] of [[90, .035], [44, .05], [16, .08], [3, .22]]) {
          g.strokeStyle = rgba(al * a); g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round';
          g.beginPath(); line.forEach((q, i) => i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1])); g.stroke();
        }
        for (const q of G.band.parts) {
          if (q[3] > k) continue;
          const p = P(q[0], q[2], q[1]); if (!p) continue;
          g.fillStyle = `rgba(255,255,255,${a * (.25 + .75 * q[4]) * (.7 + .3 * Math.sin(t * 2 + q[3] * 90))})`;
          g.beginPath(); g.arc(p[0], p[1], .6 + 1.6 * q[4], 0, 7); g.fill();
        }
      }
      const ps = G.stars.map(q => P(q[0], q[2], q[1])), n = ps.length;
      ps.forEach((p, i) => { if (!p) return; const ki = seg(k, i / Math.max(1, n) * .55, i / Math.max(1, n) * .55 + .2); if (ki > 0) star(p, G.stars[i][3], a * ki); });
      g.strokeStyle = rgba(.75 * a); g.lineWidth = 1.2;
      for (const [i, j] of G.lines) {
        const p = ps[i], q = ps[j]; if (!p || !q) continue;
        const kl = seg(k, .5 + .4 * i / Math.max(1, n), .62 + .4 * i / Math.max(1, n)); if (kl <= 0) continue;
        g.beginPath(); g.moveTo(p[0], p[1]); g.lineTo(p[0] + (q[0] - p[0]) * kl, p[1] + (q[1] - p[1]) * kl); g.stroke();
      }
    }
    g.restore();
    for (const G of SK.groups) {   // the pair of names: the star's, then the place's
      const k = seg(t, G.on + G.draw * .6, G.on + G.draw * .6 + .5), p = G.lab && P(G.lab[0], G.lab[2], G.lab[1]);
      if (k <= 0 || !p || !G.a) continue;
      txt('sky_' + G.id, G.a, p[0], p[1], 'zh_sans_strong', 26, rgba(1), a * k, { center: true, shadow: 12, ls: 4 });
      if (G.b) txt('sky_' + G.id + 'e', G.b, p[0], p[1] + 26, 'en_strong', 15, rgba(.85), a * k, { center: true, shadow: 8, ls: 1 });
    }
    return a;
  }

  // a place name on the model: the same tag as a pin; its layout (pole length, side) per stretch of time it shows (compile)
  function placeLabel(p, a, aTxt, bTxt, lay) {
    if (!p) return;
    a *= 1 - ss(seg(p[1], SUBTOP - 20, SUBTOP + 30)); if (a <= 0) return;
    tag(p[0], p[1], { text: aTxt, sub: bTxt, len: lay ? lay[0] : 170, left: lay ? lay[1] : null, col: '#dfe6ee' }, a);
  }


  // locator: the whole plate in miniature (river, today's built-up area), the era's footprint and where the camera looks
  function locator(img, a, eraRings, eraCol, eraName, camQuad) {
    if (a <= 0 || !img || !img.naturalWidth) return;
    const Wm = 300, Hm = Wm * img.naturalHeight / img.naturalWidth, X = W - 96 - Wm, Y = H - 150 - Hm;
    g.save(); g.globalAlpha = a;
    g.fillStyle = 'rgba(6,7,11,.72)'; g.fillRect(X - 12, Y - 34, Wm + 24, Hm + 46);
    g.drawImage(img, X, Y, Wm, Hm);
    g.strokeStyle = 'rgba(255,255,255,.35)'; g.lineWidth = 1; g.strokeRect(X, Y, Wm, Hm);
    for (const ring of eraRings || []) {
      g.beginPath(); ring.forEach(([u, v], i) => i ? g.lineTo(X + u * Wm, Y + v * Hm) : g.moveTo(X + u * Wm, Y + v * Hm)); g.closePath();
      g.fillStyle = eraCol + '55'; g.fill(); g.strokeStyle = eraCol; g.lineWidth = 1.6; g.stroke();
    }
    if (camQuad) {
      g.beginPath(); camQuad.forEach(([u, v], i) => i ? g.lineTo(X + u * Wm, Y + v * Hm) : g.moveTo(X + u * Wm, Y + v * Hm)); g.closePath();
      g.strokeStyle = 'rgba(255,255,255,.85)'; g.setLineDash([3, 3]); g.lineWidth = 1.2; g.stroke(); g.setLineDash([]);
    }
    g.restore();
    // the era's name right of the word LOCATOR, in the room left between them: a long name is set smaller (down to 11 px); one too
    // long even then takes the box's whole width without the word (down to 9 px), never over it
    const lk = plain(UI.locator) ? 'mono' : 'zh', room = Wm - width(UI.locator, lk, 12, 3) - 18;
    let ep = 14, word = true;
    while (eraName && ep > 11 && width(eraName, 'zh', ep, 2) > room) ep -= .5;
    if (eraName && width(eraName, 'zh', ep, 2) > room) { word = false; ep = 14; while (ep > 9 && width(eraName, 'zh', ep, 2) > Wm) ep -= .5; }
    if (word) txt(null, UI.locator, X, Y - 14, lk, 12, 'rgba(225,230,236,.55)', a, { ls: 3 });
    if (eraName) txt(null, eraName, X + Wm, Y - 14, 'zh', ep, 'rgba(240,242,245,.85)', a, { right: true, ls: 2 });
    txt(null, 'N ↑', X + Wm - 4, Y + 16, 'mono', 12, 'rgba(240,242,245,.7)', a, { right: true });
  }

  // identity label, top-left, quiet
  function identity(t, t0, t1, l1, l2) {
    const ia = env(t, t0, t1, .6, .4);
    txt('id1', l1, 96, 90, 'zh_strong', 22, '#f4f1ea', ia, { ls: 4, shadow: 10 });
    txt('id2', l2, 96, 120, 'mono', 15, 'rgba(225,230,236,.6)', ia, { ls: 1.5 });
  }

  // end card: over the white model, left-aligned block
  function endCard(t, e) {
    const a = Math.min(eo(seg(t, e.t, e.t + .25)), 1); if (a <= 0) return;
    const k = eo(seg(t, e.t, e.t + .9)), X = 120, Y = 470;
    const gr = g.createLinearGradient(0, 0, 1880, 0);   // wide enough for the long source lines
    gr.addColorStop(0, `rgba(6,7,10,${.82 * a})`); gr.addColorStop(.75, `rgba(6,7,10,${.66 * a})`); gr.addColorStop(1, 'rgba(6,7,10,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 1880, H);
    let y = Y;
    if (e.title_a) { txt('end_a', e.title_a, X, y, 'zh_strong', 66, '#f4f1ea', a, { ls: 8 }); y += 62; }
    if (e.title_b) { txt('end_b', e.title_b, X, y, 'numeral', 44, 'rgba(240,243,246,.92)', a, { ls: 1 }); y += 40; }
    g.save(); g.globalAlpha = a; g.fillStyle = e.rule || '#ffa13d'; g.fillRect(X, y + 14, 120 * k, 2); g.restore(); y += 58;
    // the first `bright` lines (the credits, or the first source line) in the brighter mono, the rest quieter
    (e.lines || []).forEach((s, i) => { const hi = i < (e.bright || 1); txt('end_l' + i, s, X, y, hi ? 'mono' : 'zh_sans', hi ? 22 : 21, hi ? 'rgba(230,234,240,.85)' : 'rgba(225,230,236,.7)', a, { ls: hi ? 2 : 1 }); y += 36; });
    // the project's credit, on every film whatever its city.yaml says (LICENSE, condition 2a: whoever publishes a film keeps it legible)
    txt('end_credit', CREDIT, X, y + 22, 'mono', 20, 'rgba(225,230,236,.66)', a, { ls: 1 });
  }

  return { g, begin, txt, width, env, scrims, readout, pin, mark, rangeLine, subtitle, identity, endCard, timelineBar, footage, caption, placeLabel, routeLabel, locator, section, sky, counters, texts: () => TX, drawn: () => DRAWN, noteDrop };
}
