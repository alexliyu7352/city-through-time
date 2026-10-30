// Small helpers: interpolation, easing, keyframe tracks (adapted from lemo-opuscar core/lib.js, MIT, (c) 2026 LemoLab; see NOTICE)
export const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const ss = t => { t = clamp(t); return t * t * (3 - 2 * t); };
export const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
export const eo = t => 1 - Math.pow(1 - clamp(t), 3);
export const ei = t => Math.pow(clamp(t), 3);

// where a picture of aspect A lands on a stage w x h (a museum page: engine/museum.js and the page's first picture, site/museum.js):
// as wide as the stage or as tall as it, whichever covers it, but at most crop stage widths wide (a phone held upright then sees a
// band across its stage, the picture's edges feathered, not a sliver of its middle) -> { w, h, x, y } in stage pixels
export function frameOf(w, h, A, crop = 1.6) {
  const pw = Math.min(Math.max(w, h * A), crop * w), ph = pw / A;
  return { w: pw, h: ph, x: (w - pw) / 2, y: (h - ph) / 2 };
}

// monotone cubic interpolation (Fritsch-Carlson)
export function monotone(keys) {
  const n = keys.length, xs = keys.map(k => k[0]), ys = keys.map(k => k[1]);
  if (n === 1) return () => ys[0];
  const d = [], m = new Array(n).fill(0);
  for (let i = 0; i < n - 1; i++) d.push((ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]));
  m[0] = d[0]; m[n - 1] = d[n - 2];
  for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
  for (let i = 0; i < n - 1; i++) {
    if (d[i] === 0) { m[i] = m[i + 1] = 0; continue; }
    const a = m[i] / d[i], b = m[i + 1] / d[i], s = a * a + b * b;
    if (s > 9) { const k = 3 / Math.sqrt(s); m[i] = k * a * d[i]; m[i + 1] = k * b * d[i]; }
  }
  return t => {
    if (t <= xs[0]) return ys[0]; if (t >= xs[n - 1]) return ys[n - 1];
    let i = 0; while (t > xs[i + 1]) i++;
    const h = xs[i + 1] - xs[i], u = (t - xs[i]) / h, u2 = u * u, u3 = u2 * u;
    return (2 * u3 - 3 * u2 + 1) * ys[i] + (u3 - 2 * u2 + u) * h * m[i] + (-2 * u3 + 3 * u2) * ys[i + 1] + (u3 - u2) * h * m[i + 1];
  };
}
// keyframes in several dimensions: [[t, [a, b, c]], ...] -> t => [...]
export function track(keys) {
  const dim = keys[0][1].length, fs = [];
  for (let j = 0; j < dim; j++) fs.push(monotone(keys.map(k => [k[0], k[1][j]])));
  return t => fs.map(f => f(t));
}
