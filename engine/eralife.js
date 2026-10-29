// When each part of a period city stands whole in the film, and the moments the viewer shows it at (engine/main.js ?view,
// tools/eraview.mjs). A part stands whole from the end of its rise (its stage: rank x span, then grow) to the start of the loss
// that takes it (compile lose:; never, for a part no loss takes). A city that loses parts has no one moment with every part
// standing (a house and the forum laid where it stood); the viewer shows real moments of the film only.

// [from, to] in film seconds: rank, the record's start (0..1); lost, the number of the loss that takes it (0: none)
export const life = (e, rank, lost) => [e.on + rank * e.span + e.grow, lost ? e.losses[lost - 1].curve[0][0] : Infinity];

// the fewest moments that between them show every part whole: each just before a loss takes a part not yet shown, the last once
// every part still standing has risen (one moment for a city that loses nothing). P: the era file's records, lost: its per-record
// loss numbers (or null); the pools (e.basins) count as parts
export function moments(e, P, lost) {
  const iv = P.map((p, i) => life(e, p[10], lost ? lost[i] : 0)).concat((e.basins || []).map(b => life(e, b.rank, b.lost))).sort((a, b) => a[1] - b[1]);
  const out = []; let t = -Infinity;
  for (const [a, b] of iv) {
    if (a <= t && t < b) continue;
    t = b === Infinity ? iv.reduce((m, v) => v[1] === Infinity ? Math.max(m, v[0]) : m, a) + .05 : Math.max(a, b - .05);
    t = Math.round(t * 100) / 100; out.push(t);
  }
  return out;
}

// the record stands whole at t
export const whole = (e, rank, lost, t) => { const [a, b] = life(e, rank, lost); return a <= t && t < b; };
