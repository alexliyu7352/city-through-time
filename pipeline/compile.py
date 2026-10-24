"""city.yaml (node-based) + build/data/stats.json -> build/film.json (what engine/main.js plays), build/data/layers*.png (epoch
masks), build/data/decal_*.png (graphics on the plate), build/export/subtitles.json (subtitles for srt.py). Paths: pipeline/layout.py.
usage: python -I pipeline/compile.py <city_dir>

The film is a sequence of NODES. Each node has a year (or a year range the counter runs through), a duration in seconds and its own
layers, pins, cues and camera keys with times RELATIVE to the node's start. The compiler lays nodes out one after another, so the
film's length is the sum of its nodes (plus the opening and the closing), never a number chosen first.
Times inside a node: seconds from the node start (`at: 2.5`), `{year: Y}` (resolved on the node's own year ramp), or `end` (the node's end).
Text: `{expr}` is evaluated with `stats` (data/stats.json), `n(x)`, `pct(x)`."""
import random, json, os, sys, re, math
import yaml
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from types import SimpleNamespace
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import Frame
import decals as DEC
import citygen
import stagecraft

class Seen(dict):
    """a city.yaml mapping that remembers which of its keys were read: a key nothing reads is a typo, or one this version
    does not have, and is skipped without a word (the user, 2026-10-22: 'with:' on an area was never passed on). Listed at the end"""
    def __getitem__(self, k): self.read.add(k); return super().__getitem__(k)
    def get(self, k, d=None): self.read.add(k); return super().get(k, d)
    def __contains__(self, k): self.read.add(k); return super().__contains__(k)
    def setdefault(self, k, d=None): self.read.add(k); return super().setdefault(k, d)
    def pop(self, k, *d): self.read.add(k); return super().pop(k, *d)
    def __iter__(self): self.read.update(dict.keys(self)); return super().__iter__()
    def keys(self): self.read.update(dict.keys(self)); return super().keys()
    def items(self): self.read.update(dict.keys(self)); return super().items()
    def values(self): self.read.update(dict.keys(self)); return super().values()
class _SeenLoader(yaml.SafeLoader): pass
def _seen_map(loader, node):
    d = Seen(); d.read = set(); yield d
    d.update(loader.construct_mapping(node)); d.mine = set(dict.keys(d))   # (keys compile adds later are not the author's)
_SeenLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _seen_map)
WARN = []   # warnings on the settings, said once at the end (compile runs again for each pass of the stage plan)

D = os.path.abspath(sys.argv[1])
C = yaml.load(open(os.path.join(D, 'city.yaml'), encoding='utf-8'), Loader=_SeenLoader)
import layout as LAYOUT
ST = json.load(open(LAYOUT.data(D, 'stats.json'), encoding='utf-8'))
# a position more than a plate's width beyond the plate (and the land beyond it, terrain.context) is a typo and stops compile
# (咸阳: the tiger tally at lat 45.0, 1200 km north, found only by stills of every second)
F = Frame(tuple(C['box']), 1.0 / C['scale'], near=[b_ for b_ in [((C.get('terrain') or {}).get('context') or {}).get('box')] if b_])
FM = C['film']
LAYOUT.ensure(D)
LANG = FM.get('lang', ['zh', 'en'])
# the languages (pipeline/i18n.py, i18n/<code>.yaml): one or two, any that has a pack; the program's own words come from the packs
import i18n
if not 1 <= len(LANG) <= 2: raise SystemExit(f'compile: film.lang {LANG}: one or two languages (the first line and the second line)')
PACK = [i18n.pack(l_) for l_ in LANG]
SCRIPTS = [P_['script'] for P_ in PACK]
# the words come from script.yaml (pipeline/script.py): each node's lines become its cues; city.yaml holds pictures only
import script as SCRIPT
SCR = SCRIPT.load(D, LANG, [nd['id'] for nd in FM['nodes']])
if SCR is not None:
    for nd in FM['nodes']:
        if nd.get('cues'): raise SystemExit(f'compile: node {nd["id"]} has cues in city.yaml and the city has a script.yaml: the words belong in script.yaml only')
        nd['cues'] = SCR['nodes'].get(nd['id'], [])
    if (FM.get('opening') or {}).get('cue'): raise SystemExit('compile: film.opening.cue in city.yaml and a script.yaml: the opening line belongs in script.yaml (opening:)')
    if SCR['opening']: FM.setdefault('opening', {})['cue'] = SCR['opening'][0]

# the narrator's arc and the emblem (SKILL.md 步驟 3-4; the user, 2026-10-20/21): every node says what the narrator feels there,
# and the film says whether it has an emblem. They drive the copy, the music and the picture (build/export/timeline.json)
MOODS = {'wonder': 'the land and its first people: curiosity, awe', 'pride': 'the city flourishes, a hero appears',
         'grief': 'decline, destruction, a loss', 'wistful': 'what was hoped for and did not come, a farewell',
         'hope': 'a new town rises, a new start', 'calm': 'the city goes on, quietly'}
def node_mood(nd):
    m_ = nd.get('mood')
    if m_ is None: raise SystemExit(f'compile: node {nd["id"]} has no mood: the narrator\'s feeling there, one of {", ".join(MOODS)} (mood: pride or {{feel: pride, level: 3}})')
    feel_, lvl_ = (m_, 2) if isinstance(m_, str) else (m_.get('feel'), m_.get('level', 2))
    if feel_ not in MOODS: raise SystemExit(f'compile: node {nd["id"]}: mood {feel_!r} (one of: ' + '; '.join(f'{k} = {v}' for k, v in MOODS.items()) + ')')
    if lvl_ not in (1, 2, 3): raise SystemExit(f'compile: node {nd["id"]}: mood level {lvl_!r} (1 quiet, 2, 3 strongest)')
    return {'feel': feel_, 'level': lvl_}
for nd in FM['nodes']: nd['_mood'] = node_mood(nd)
EMBLEM = FM.get('emblem')
if EMBLEM is None: raise SystemExit("compile: film.emblem: say whether the city has one (emblem: none, or {name, meaning, nodes: [...]}: SKILL.md 步驟 3)")
if EMBLEM != 'none':
    if not isinstance(EMBLEM, dict) or not EMBLEM.get('name') or not EMBLEM.get('meaning'): raise SystemExit('compile: film.emblem: {name, meaning, nodes} (what it personifies, said once in words)')
    _bad = [n_ for n_ in EMBLEM.get('nodes', []) if n_ not in [nd['id'] for nd in FM['nodes']]]
    if _bad: raise SystemExit(f'compile: film.emblem.nodes: no node {", ".join(_bad)}')
# the emblem on the plate (tally keys) only where the film has one: the template's tiger tally outlived its storyline (咸阳, 2026-10-21)
_tally_at = [k_ for k_ in ('opening', 'closing') if (FM.get(k_) or {}).get('tally')] + [nd['id'] for nd in FM['nodes'] if nd.get('tally')]
if EMBLEM == 'none' and _tally_at: raise SystemExit(f'compile: film.emblem is none, but there are emblem keys (tally) in {", ".join(_tally_at)}: drop them, or give the film its emblem')
if EMBLEM != 'none' and [n_ for n_ in _tally_at if n_ not in ('opening', 'closing') and n_ not in EMBLEM.get('nodes', [])]:
    WARN.append(f'emblem keys (tally) in {", ".join(n_ for n_ in _tally_at if n_ not in ("opening", "closing") and n_ not in EMBLEM.get("nodes", []))}, '
                f'which film.emblem.nodes does not list: the emblem shows where its story is not told')
# the film ends on this year (SKILL.md 步驟 3), and a stop's colour ring must read against the one before (咸阳: the Qin orange
# and the empire's first colour were one, and the ring that should repaint the city did not show): Lab ΔE76 under 25 is too close,
# unless the two are one chapter in one colour (the stops of the modern growth), which two period cities never are
import datetime
_ylast = (FM['nodes'][-1].get('years') or [None])[-1] if FM['nodes'] else None
if _ylast is not None and _ylast != datetime.date.today().year:
    WARN.append(f'the last stop, {FM["nodes"][-1]["id"]}, ends in {_ylast}, not this year ({datetime.date.today().year}): the film ends today')
def _lab(h):
    r_, g_, b_ = [(c_ / 12.92 if c_ <= .04045 else ((c_ + .055) / 1.055) ** 2.4) for c_ in (int(h.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4))]
    f_ = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    X_, Y_, Z_ = f_((r_ * .4124 + g_ * .3576 + b_ * .1805) / .95047), f_(r_ * .2126 + g_ * .7152 + b_ * .0722), f_((r_ * .0193 + g_ * .1192 + b_ * .9505) / 1.08883)
    return 116 * Y_ - 16, 500 * (X_ - Y_), 200 * (Y_ - Z_)
for a_, b_ in zip(FM['nodes'], FM['nodes'][1:]):
    if not (a_.get('col') and b_.get('col')): continue
    d_ = math.dist(_lab(a_['col']), _lab(b_['col']))
    if 0 < d_ < 25 or (d_ < 25 and 'city' in a_ and 'city' in b_):
        WARN.append(f'{a_["id"]} {a_["col"]} and {b_["id"]} {b_["col"]} are {d_:.0f} apart (Lab ΔE, 25 or more reads): the colour ring '
                    f'into {b_["id"]} will not show; move them apart, or give them one colour if they are one chapter')

# a period city drawn over an old map or a site plan (city.trace, pipeline/citygen.py traced): its features join the city's own
# walls, streets, blocks and landmarks for every step that reads them (the reads still count on the city as written: Seen)
for nd in FM['nodes']:
    cs = nd.get('city')
    if cs and cs.get('trace'):
        add_ = citygen.traced(cs, F, D); cs_ = Seen(dict.items(cs)); cs_.read, cs_.mine = cs.read, cs.mine
        for k_, v_ in add_.items():
            if v_: cs_[k_] = list(cs.get(k_, [])) + v_
        nd['city'] = cs_

# ------------------------------------------------------------------ text templates and positions
def _ns(o): return SimpleNamespace(**{str(k): _ns(v) for k, v in dict.items(o)}) if isinstance(o, dict) else [_ns(v) for v in o] if isinstance(o, list) else o
STN = _ns(ST)
def n(x): return f'{int(round(x)):,}'
def pct(x): return str(int(round(x * 100)))
# numbers the picture shows that come from the city's own settings and shapes (SKILL.md 步驟 4: never written by hand, so they
# follow when a factor or an outline changes): cfg = city.yaml ({cfg.terrain.exaggeration:g}), plate_km = the plate's
# [width, depth] in km, km(id) = a line's length or an outline's perimeter in km, km2(id) = an outline's area in km²; the ids
# are a researched area's (film.areas_file), an epoch's or a line's
CFG = None
def _shape(id_):
    from shapely.geometry import Polygon as _Pg, LineString as _Ls, Point as _Pt
    from shapely.ops import unary_union
    U = lambda ring: [F.to_utm.transform(*q[:2]) for q in ring]
    for nd in FM['nodes']:
        for e in nd.get('epochs', []):
            if e.get('id') != id_: continue
            parts_ = [_Pg(U(r)) for r in e.get('polygons', [])] + [_Pg(U(r)) for nm_ in e.get('osm_polygons', []) for r in osm_rings(nm_)]
            parts_ += [_Pt(*F.to_utm.transform(c[0], c[1])).buffer(c[2]) for c in e.get('circles', [])]
            return unary_union([p_.buffer(0) for p_ in parts_])
        for L in nd.get('lines', []):
            if L.get('id') == id_ and L.get('polylines'): return unary_union([_Ls(U(pl)) for pl in L['polylines']])
    try: rings_ = area_rings(id_)
    except SystemExit: rings_ = []
    if not rings_: raise SystemExit(f'compile: km({id_!r}) / km2({id_!r}): no epoch, line or researched area with that id has a shape')
    return unary_union([_Pg(U(r)).buffer(0) for r in rings_])
def km(id_): g_ = _shape(id_); return (g_.length if g_.geom_type in ('LineString', 'MultiLineString') else g_.exterior.length if g_.geom_type == 'Polygon' else sum(p_.exterior.length for p_ in g_.geoms)) / 1000
def km2(id_): return _shape(id_).area / 1e6
def _fill(m):
    global CFG
    expr = m.group(1); fmt = None
    if ':' in expr and re.match(r'^[^:]+:[-+ 0-9.,%a-zA-Z]*$', expr): expr, fmt = expr.rsplit(':', 1)
    if CFG is None: CFG = _ns(C)   # (dict.items: reading it for a number does not count as reading every key)
    v = eval(expr, {'stats': STN, 'n': n, 'pct': pct, 'round': round, 'int': int, 'len': len, 'cfg': CFG,   # noqa: S307 (authored config)
                    'plate_km': [(F.x1 - F.x0) / 1000, (F.y1 - F.y0) / 1000], 'km': km, 'km2': km2})
    return format(v, fmt) if fmt else str(v)
def tx(s): return re.sub(r'\{([^{}]+)\}', _fill, s) if isinstance(s, str) else s
_LANGS_ANY = {f_[:-5] for f_ in os.listdir(os.path.join(i18n.ROOT, 'i18n')) if f_.endswith('.yaml')} | {'zh', 'en'}
MISSING = []   # texts written for some language but not for one the film shows (compile stops on them once through)
def ab(o):
    """a text's first and second language (film.lang); a text written in some language but not in one of the film's is listed"""
    if isinstance(o, dict) and any(k_ in _LANGS_ANY for k_ in o):
        for l_ in LANG:
            if not o.get(l_): MISSING.append((l_, str(o.get('id') or next((o[k_] for k_ in o if k_ in _LANGS_ANY and o[k_]), ''))[:40]))
    a = tx(o.get(LANG[0])); b = tx(o.get(LANG[1])) if len(LANG) > 1 else None
    return a, b
def pick(v):
    """a text written once (in the first language) or per language ({zh: .., en: ..}): the first language's"""
    if isinstance(v, dict) and any(k_ in _LANGS_ANY for k_ in v):
        if not v.get(LANG[0]): MISSING.append((LANG[0], str(next(iter(v.values()), ''))[:40]))
        return tx(v.get(LANG[0]))
    return tx(v)
def hold(s):
    if not s: return 0
    return i18n.reading_time(s)   # (per writing system: Han and kana, hangul, alphabets; the Han and Latin rates as before)
def pos_of(o):
    if 'pos' in o: return o['pos']
    if 'mark' in o and o['mark'] in PROP_MARKS: return PROP_MARKS[o['mark']]
    if 'mark' in o: return ST['marks'][o['mark']]['pos']
    if 'lon' in o:   # h_m above the ground there (a pin on the plateau stands on the plateau, not at the plate's zero)
        x, z = F.model_lonlat(o['lon'], o['lat']); return [x, z, round(ground_ll(o['lon'], o['lat']) + o.get('h_m', 0) * F.scale, 6)]
    raise ValueError(f'no position in {o}')

# ------------------------------------------------------------------ terrain sampler (same field prep.py used), for prop and pin heights
TER = None
if os.path.exists(LAYOUT.data(D, 'terrain.png')) and C.get('terrain', {}).get('enabled', True):
    import terrainio
    _timg, _tj = terrainio.load(D)
    _tex = float(C.get('terrain', {}).get('exaggeration', 3.0))
    _cimg, _cj = terrainio.load_context(D)   # the land beyond the plate (terrain.context): pins may stand on it
    CTX_RECT = _cj['rect_model'] if _cj else None   # [x0, x1, z0, z1] model units
    _CTXC = (C.get('terrain') or {}).get('context') or {}
    _CTXX = float(_CTXC.get('exaggeration_far', _tex)); _CTXB = float(_CTXC.get('blend_km', 6)) * 1000 * F.scale
    def ground_ll(lon, lat):
        x, y = F.to_utm.transform(lon, lat); u, v = F.uv(x, y)
        if _cimg is not None and not (0 <= u <= 1 and 0 <= v <= 1):
            cx0, cx1, cy0, cy1 = _cj['rect_utm']
            if cx0 <= x <= cx1 and cy0 <= y <= cy1:   # the engine's exaggeration there: the plate's at its edge, exaggeration_far beyond blend_km
                mx, mz = F.model(x, y); out = math.hypot(max(0, abs(mx) - F.size[0] / 2), max(0, abs(mz) - F.size[1] / 2))
                k = min(1.0, out / _CTXB); ex = _tex + (_CTXX - _tex) * k * k * (3 - 2 * k)
                return terrainio.bilinear(_cimg, (x - cx0) / (cx1 - cx0), (cy1 - y) / (cy1 - cy0)) * F.scale * ex
        return terrainio.bilinear(_timg, u, v) * F.scale * _tex
    def ground_m_xy(x, y):
        u, v = F.uv(x, y); return terrainio.bilinear(_timg, u, v)
    # the ground as the engine draws it (terrainio.plate_mesh): where the ground dips between the plate mesh's corners the
    # plate stands above the sampled ground, and a period city laid on the sampled ground loses its thin parts under the plate
    # (a road 12 cm thick came out in dashes). citygen lays on this.
    _PLATE = terrainio.plate_mesh(_timg, *F.size)
    def ground_m_mesh(x, y):
        u, v = F.uv(x, y); return _PLATE((u - .5) * F.size[0], (v - .5) * F.size[1])
    _ttrue, _ = terrainio.load(D, true=True)
    def section_profile(a_ll, b_ll, n=120):
        """a terrain section's profile in metres above sea level, n points from a to b, from the relief as measured (the plate's
        fine relief is drawn smaller: terrain.py), so the heights it prints are the land's: {profile, lo, hi} as the engine
        would otherwise sample them off the plate (main.js)"""
        (ax, ay), (bx, by) = F.to_utm.transform(*a_ll), F.to_utm.transform(*b_ll)
        pr = [round(_tj['min_m'] + terrainio.bilinear(_ttrue, *F.uv(ax + (bx - ax) * k / (n - 1), ay + (by - ay) * k / (n - 1))), 2) for k in range(n)]
        return {'profile': pr, 'lo': round(min(pr) - 8, 2), 'hi': round(max(pr) + 12, 2)}
else:
    def ground_ll(lon, lat): return 0.0
    def ground_m_xy(x, y): return 0.0
    ground_m_mesh = ground_m_xy
    def section_profile(a_ll, b_ll, n=120): return {}
    _tex = 3.0; _cj = None; CTX_RECT = None

# ------------------------------------------------------------------ OSM geometry by name (all cached themes)
import osmgeo
import local
OSM = osmgeo.elements(local.raw())
def osm_rings(name): return osmgeo.rings(OSM, name)

_MODEL = json.load(open(LAYOUT.data(D, 'model.json')))
FOOT = {}
HW = 4096; HH = round(HW * F.size[1] / F.size[0])   # hide masks: ~7.6 m per pixel at Xianyang's plate
def era_boundary(prims, cs):
    """the period city's outline on the plate: the union of its ground-level bodies (no trees, water or paving), closed over
    gaps up to `boundary_close_m` and opened again by 70 % of it (so it sits ~30 % of that outside the outermost building),
    small islands dropped, simplified. Rings in model units [[x, z], ...]: the glowing frame, the ground fill and the hide mask."""
    import shapely as _sh
    S = F.scale; feet = []
    for p in prims:
        if p[4] > p[12] + 1e-9 or p[11] in (4, 5, 7): continue
        t, cx, cz, rot = p[0], p[1], p[2], p[3]
        hw, hd = (max(p[5], p[8] if t == 2 else 0) / 2 + (p[8] if t == 1 else 0), max(p[6], p[9] if t == 2 else 0) / 2) if t in (0, 1, 2) else (p[5], p[5])
        c_, s_ = math.cos(rot), math.sin(rot)
        feet.append([(cx + x * c_ - z * s_, cz + x * s_ + z * c_) for x, z in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd))])
    if not feet: return []
    R = cs.get('boundary_close_m', 70) * S
    # grow every footprint first, then union (the union of grown rectangles is simple; buffering a union of 30k pieces takes minutes)
    g = _sh.union_all(_sh.buffer(_sh.polygons(feet), R, join_style='mitre')).buffer(-R * .7, join_style='mitre')
    if cs.get('outline'):   # an outline the buildings do not give (a village's ditch): joined into the city's outline
        g = g.union(_sh.union_all([_sh.Polygon([F.model_lonlat(lon, lat) for lon, lat in r]) for r in cs['outline']]))
    polys = [q for q in getattr(g, 'geoms', [g]) if q.area >= (cs.get('boundary_min_m', 140) * S) ** 2]
    return [[[round(x, 5), round(z, 5)] for x, z in q.simplify(8 * S).exterior.coords] for q in polys]

EW = 1024   # edge distance fields: one era per channel, each over its own crop of the plate (edge.png, edge2.png)
EDGES = []   # per era: [image, crop rect in plate uv]

def edge_sdf(bnd, D):
    """distance to the era's outline, in units of D (0 on the line, 1 at D or beyond), over the outline's bounding box (+D).
    A distance field stays smooth when the camera comes close (a blurred mask shows its pixels); the engine draws the
    thin line with geometry and uses this only to light what stands near it."""
    import numpy as _np, shapely as _sh
    if not bnd: return Image.new('L', (EW, EW), 255), [0, 0, 0, 0]
    lines = _sh.union_all([_sh.LinearRing(r) for r in bnd if len(r) >= 3]); _sh.prepare(lines)
    xs_ = [x for r in bnd for x, _ in r]; zs_ = [z for r in bnd for _, z in r]
    x0, x1, z0, z1 = min(xs_) - D, max(xs_) + D, min(zs_) - D, max(zs_) + D
    gx = x0 + (_np.arange(EW) + .5) / EW * (x1 - x0); gz = z0 + (_np.arange(EW) + .5) / EW * (z1 - z0)
    X, Z = _np.meshgrid(gx, gz); pts = _sh.points(X.ravel(), Z.ravel())
    near = _sh.dwithin(pts, lines, D); d = _np.full(X.size, D)
    d[near] = _sh.distance(pts[near], lines)
    img = Image.fromarray((_np.clip(d / D, 0, 1) * 255).round().astype(_np.uint8).reshape(EW, EW), 'L')
    PWm, PDm = F.size
    return img, [round(x0 / PWm + .5, 6), round(z0 / PDm + .5, 6), round(x1 / PWm + .5, 6), round(z1 / PDm + .5, 6)]

def rect_of(p, pad=0.0):
    """a primitive's footprint corners (model xz), padded"""
    t, cx, cz, rot = p[0], p[1], p[2], p[3]
    if t in (0, 1, 2): hw = max(p[5], p[8] if t == 2 else 0) / 2 + pad + (p[8] if t == 1 else 0); hd = max(p[6], p[9] if t == 2 else 0) / 2 + pad
    else: hw = hd = p[5] + pad
    c_, s_ = math.cos(rot), math.sin(rot)
    return [(cx + x * c_ - z * s_, cz + x * s_ + z * c_) for x, z in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd))]

def hide_layer(prims, cs, bnd=()):
    """where an era city stands, today's buildings step aside. The value is .04 + .96 x the rank (start time, 0..1 over the
    era's rise) of the era building at that spot, so today's building there sinks just before the old one beside it rises,
    in whatever order the stages grow (engine: hideK). Covers every primitive's padded footprint, today's buildings that
    touch the era city (their whole footprint), the city's outline and explicit hide regions; gaps inside take the rank of
    the nearest era building."""
    import numpy as _np
    PWm, PDm = F.size
    pad = cs.get('hide_buffer_m', 14) * F.scale
    U_ = lambda X, Z: ((X / PWm + .5) * HW, (Z / PDm + .5) * HH)
    code = lambda r: max(10, int(round((.04 + .96 * r) * 255)))
    im = Image.new('L', (HW, HH), 0); dr = ImageDraw.Draw(im)
    for p in sorted(prims, key=lambda q: -q[10]):   # the earliest rank wins where footprints overlap: drawn last
        dr.polygon([U_(x, z) for x, z in rect_of(p, pad)], fill=code(p[10]))
    FOOT[cs.get('_id', '')] = im.point(lambda v: 255 if v else 0)   # the era's own footprint (the finale's fallback)
    try:   # whole buildings of today that touch the era city step aside with the earliest era building they touch
        from shapely.geometry import Polygon as _P
        from shapely.strtree import STRtree as _T
        ground = [p for p in prims if p[4] <= p[12] + 1e-9 and p[11] not in (4, 5, 7)]
        if ground:
            tree = _T([_P(rect_of(p)) for p in ground]); rk = _np.array([p[10] for p in ground])
            for b in _MODEL['p']:
                ring = b[2][0]
                if len(ring) < 3: continue
                hit = tree.query(_P(ring), predicate='intersects')
                if len(hit): dr.polygon([U_(x, z) for x, z in ring], fill=code(float(rk[hit].min())))
    except Exception as ex:
        print('hide: today-overlap pass skipped', ex)
    reg = Image.new('L', (HW, HH), 0); dg = ImageDraw.Draw(reg)
    for r in [w['ring'] for w in cs.get('walls', []) if 'ring' in w] + cs.get('hide', []): dg.polygon([U_(*F.model_lonlat(lon, lat)) for lon, lat in r], fill=255)
    for r in bnd: dg.polygon([U_(x, z) for x, z in r], fill=255)
    val = _np.asarray(im).astype(_np.float32); region = (_np.asarray(reg) > 0) | (val > 0)
    region = _np.asarray(Image.fromarray(region.astype(_np.uint8) * 255).filter(ImageFilter.MaxFilter(3))) > 0   # one pixel of margin: a building whose centre sits on the edge
    ys, xs = _np.nonzero(region)
    if len(xs):   # fill the gaps inside with the nearest rank (3x3 min growing outward, on the region's crop only)
        y0, y1, x0, x1 = max(0, ys.min() - 2), min(HH, ys.max() + 3), max(0, xs.min() - 2), min(HW, xs.max() + 3)
        a = _np.where(val[y0:y1, x0:x1] > 0, val[y0:y1, x0:x1], _np.inf); rg = region[y0:y1, x0:x1]
        for _ in range(80):
            if not (_np.isinf(a) & rg).any(): break
            P_ = _np.pad(a, 1, constant_values=_np.inf)
            m_ = _np.minimum.reduce([P_[1 + dy:P_.shape[0] - 1 + dy, 1 + dx:P_.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)])
            a = _np.where(_np.isinf(a) & rg, m_, a)
        a = _np.where(rg & _np.isinf(a), 255, a); a = _np.where(rg, a, 0)
        val[y0:y1, x0:x1] = a
    return Image.fromarray(_np.clip(val, 0, 255).round().astype(_np.uint8), 'L')

TIMING = {'ring_view': 2.8, 'ring_out': 1.6, 'min_stage': 4.0, 'min_stage_small': 2.0, 'grow': 1.6, 'frames_per_s': 1 / 3,
          'settle_need': 2.0, 'ring_m': 1000.0, 'ring_q': .35, 'scan_w': .12, 'fade': .4, 'fall_dur': 1.4,
          'hold_after': 2.5, 'look_size': .4, 'look_secs': 3.5, 'look_focus_m': 400.0, 'look_min_n': 30,
          'ring_fit_x': .9, 'ring_fit_y': .85, 'ruins_d': .3, 'contract_in': 2.0,
          'see_rate': .002, 'see_min': 2.0, 'see_max': 12.0,
          'dead_air_s': 3.0, 'word_gap_s': 5.0}   # today's buildings that come into view together rise one after another
                                                              # over see_rate s each, see_min..see_max s in all (was .0012, 0..8: too fast, the user 2026-10-21)
# time the algorithm inserts into nodes (SKILL.md 演出文法 9e): {node id: [{tau: node seconds, delta: s, keys: [[offset s, key]], why}]};
# compile re-runs itself with the plan until nothing more is needed
PLAN = json.loads(os.environ.get('CT_PLAN') or '{}'); PASS = int(os.environ.get('CT_PASS') or 1)
TIMING.update(FM.get('timing', {}))

def model_ground(x, z):
    """the plate's height (model units) under a model point"""
    return ground_m_xy(x / F.scale + F.cx, -z / F.scale + F.cy) * F.scale * _tex

def stage_parts(prims, meta, cs, node_id):
    """the city's buildings by stage: G {group id: {tag, c (model xz centre)}} and [(stage, first, [group ids]), ...] in the
    order the stages claim them (stages with a `select` first, then the rest; `first` = the first stage in spec order, the
    one a beam lands on). A stage names its parts by `id` or `group` (list indices shift when a part is added: refused)."""
    stages = cs.get('stages') or [{}]
    G = {}
    for p, (gid, tag, _) in zip(prims, meta):
        G.setdefault(gid, {'tag': tag, 'c': (p[15], p[16])})
    def resolve(sel):
        out = {}
        for cat, v in sel.items():
            if v is True: out[cat] = True; continue
            items = cs.get(cat) if isinstance(cs.get(cat), list) else []
            idx = []
            for name in v:
                if not isinstance(name, str):
                    raise SystemExit(f'compile: era {node_id}: stage select {cat}: {name!r} is an index; give the part an id (or group) and name it')
                hit = [i for i, it in enumerate(items) if isinstance(it, dict) and name in (it.get('id'), it.get('group'))]
                if not hit: raise SystemExit(f'compile: era {node_id}: stage select {cat}: no part with id or group {name!r}')
                idx += hit
            out[cat] = idx
        return out
    def match(sel, tag):
        v = sel.get(tag[0]); return v is True or (isinstance(v, list) and tag[1] in v)
    stages = [dict(st, select=resolve(st['select'])) if st.get('select') else st for st in stages]
    taken, order = set(), []
    for st in [x for x in stages if x.get('select')] + [x for x in stages if not x.get('select')]:
        gids = [g for g, v in G.items() if g not in taken and (not st.get('select') or match(st['select'], v['tag']))]
        if not gids: continue
        taken.update(gids); order.append((st, st is stages[0], gids))
    return G, order

LOOK_NEVER = {'ditch', 'pool', 'pool_ring', 'kilns', 'boats', 'corridor', 'chimney', 'village', 'paifang'}   # not a building to look at
LOOK_WALLED = {'palace', 'court', 'office', 'temple', 'market', 'armoury', 'platform'}   # a precinct drawn by its lit walls

def look_target(G, gids, cs, node_id, traced):
    """where a closer look at a stage goes (plan_stages c), by rank (SKILL.md 演出文法 9c):
    1. a landmark the film names (a pin of its node within 250 m); 2. a key building drawn in light: a walled precinct, or any
    landmark of a small place traced by its outline (`traced`); 3. any other landmark. Largest first within a rank. Never
    the houses (fabric) or a low-detail part made to be seen from the air; None when the stage has nothing to look at."""
    node_ = next(n for n in FM['nodes'] if n['id'] == node_id)
    pins_ = [F.model_lonlat(p['lon'], p['lat']) for p in node_.get('pins', []) if 'lon' in p]
    lm_, by_ = cs.get('landmarks') or [], {}
    for g in gids:
        cat, li = G[g]['tag']
        if cat != 'landmarks' or li >= len(lm_): continue
        spec = lm_[li]
        if spec.get('kind') in LOOK_NEVER or spec.get('detail', cs.get('detail')) == 'low': continue
        by_.setdefault(li, []).append(G[g]['c'])
    best = None
    for li, cc in by_.items():
        spec = lm_[li]; x_ = sum(c[0] for c in cc) / len(cc); z_ = sum(c[1] for c in cc) / len(cc)
        rank = 1 if any(math.hypot(x_ - px, z_ - pz) <= 250 * F.scale for px, pz in pins_) else 2 if (traced or spec.get('kind') in LOOK_WALLED) else 3
        size = float(spec.get('w_m', 0)) * float(spec.get('d_m', spec.get('w_m', 0)))
        key = (rank, -size)
        if best is None or key < best[0]: best = (key, (x_, model_ground(x_, z_), z_), spec.get('id') or spec.get('kind'))
    return None if best is None else {'c': best[1], 'rank': best[0][0], 'what': best[2]}

def era_times(prims, meta, cs, at_of, cam, t_lo, t_hi, impact=None, node_id=''):
    """when each building of a period city starts to rise (absolute seconds) and how each stage is lit (SKILL.md 演出文法).
    `stages` in the spec, each with at, dur, select ({landmarks: [i..], fabric: [i..], walls/streets/lanes/trees: true or
    [i..]}; omitted = everything not claimed yet), an order (from [lon, lat]: radial; sweep [[lon, lat], [lon, lat]]: along
    a line) and noise. Without stages: one stage over everything.
    at: seconds in the node, {after: route} (when the beam lands), or auto (default): the first moment from the beam's landing
    (`impact`: the node's beam, if any) or the node start on which the camera holds the stage's buildings in view (stagecraft.
    settle); compile stops with an error when the camera never does.
    The lighting follows the size on screen (stagecraft.choose_mode): a ring from the origin (from the beam's landing point
    when there is a beam), a sweeping line, or a band scanning across a small place inside its outline. A stage lasts at
    least TIMING min_stage seconds and its front crosses no more than a third of the frame per second."""
    G, order = stage_parts(prims, meta, cs, node_id)
    grow = float(cs.get('grow', TIMING['grow']))
    start, fronts = {}, []
    for st, first, gids in order:   # (the beam lands on the city's first stage in spec order)
        C = [G[g]['c'] for g in gids]
        cx_ = sum(c[0] for c in C) / len(C); cz_ = sum(c[1] for c in C) / len(C)
        rad_ = max(math.hypot(x - cx_, z - cz_) for x, z in C) + 30 * F.scale
        centre = (cx_, model_ground(cx_, cz_), cz_)
        if 'sweep' not in st:   # a change that starts from a point (from, the beam's landing, the city's origin): the viewer must see that point
            ox_, oz_ = F.model_lonlat(*st['from']) if 'from' in st else impact['end'] if (first and impact) else F.model_lonlat(*cs['origin'])
            centre = (ox_, model_ground(ox_, oz_), oz_); rad_ = max(math.hypot(x - ox_, z - oz_) for x, z in C) + 30 * F.scale
        at = st.get('at', cs.get('at', 'auto'))
        if first and impact and impact.get('follow') and at in ('auto', 'arrive'):   # the camera rode the beam down and turned to
            t0 = round(impact['arrive'] + .1, 3); t_from = t0                       # the whole city: it grows from there
        else:   # the camera decides: the first moment it holds the place, from the beam's landing or the node start; a start set
            # by hand (seconds, {after: route}) is only the earliest it may begin (SKILL.md 演出文法 9a)
            auto_ = at in ('auto', 'arrive') or (isinstance(at, dict) and 'arrive' in at)
            t_from = max(t_lo, impact['land'] if impact else t_lo) if auto_ else at_of(at)
            t0 = stagecraft.settle(cam, centre, rad_, t_from, t_hi, need=TIMING['settle_need'], hidden=covered)
            if t0 is None:   # held only for a moment: start there, and the planner holds the camera (plan_stages b)
                t0 = stagecraft.settle(cam, centre, rad_, t_from, t_hi, need=.3, hidden=covered)
            if t0 is None:
                print(f'    stage {st}: {len(gids)} buildings, centre {centre}, radius {rad_:.4f}; camera target at {t_from:.1f}: {[round(v, 4) for v in cam.at(t_from)[1]]}')
                tt_ = t_from
                while tt_ <= t_hi: print('   ', stagecraft.settle_report(cam, centre, rad_, tt_)); tt_ += max(.5, (t_hi - t_from) / 24)
                raise SystemExit(f'compile: era {node_id}: the camera never holds the city in view between {t_from:.1f} and {t_hi:.1f} s '
                                 f'(needs {TIMING["settle_need"]} s with the place in the central 60 % of the frame, at least 12 % of its height, '
                                 f'and a camera that is not leaving): add a camera key that frames it')
            if not auto_ and t0 > t_from + 3: print(f'  note: era {node_id}: a stage asked for {t_from:.1f} s starts at {t0:.1f} s, when the camera holds it')
            t0 = round(t0 + .2, 3)
        # the order and the light: a sweep along a line; else from a point (the beam's landing for the first stage of a city
        # a beam lands on), as a ring when the place is large on screen, as a scanning band inside the outline when small
        if 'sweep' in st:
            (ax, az), (bx, bz) = F.model_lonlat(*st['sweep'][0]), F.model_lonlat(*st['sweep'][1]); L = math.hypot(bx - ax, bz - az) or 1e-9
            dx, dz = (bx - ax) / L, (bz - az) / L
            pr = [(x - ax) * dx + (z - az) * dz for x, z in C]; p0, p1 = max(0.0, min(pr)), min(L, max(pr))
            u = [min(1, max(0, (v - p0) / ((p1 - p0) or 1))) for v in pr]
            mode, o, dirv, r0, r1, length = 'line', [ax, az], [dx, dz], p0, p1, p1 - p0
        else:
            if 'from' in st: ox, oz = F.model_lonlat(*st['from'])
            elif first and impact: ox, oz = impact['end']
            else: ox, oz = F.model_lonlat(*cs['origin'])
            d = [math.hypot(x - ox, z - oz) for x, z in C]; d0, d1 = min(d), max(d)
            mode = st.get('mode') or stagecraft.choose_mode(cam, t0, centre, d1 / F.scale, F.scale, TIMING['ring_m'], TIMING['ring_q'])
            if mode == 'ring':
                u = [(v - d0) / ((d1 - d0) or 1) for v in d]; o, dirv, r0, r1, length = [ox, oz], None, d0, d1, d1 - d0
            else:   # scan: a band across the place, from the side the beam came from (else from the west)
                if impact and first: dx, dz = impact['dir']
                else: dx, dz = st.get('scan_dir', (1.0, 0.0))
                n_ = math.hypot(dx, dz) or 1; dx, dz = dx / n_, dz / n_
                pr = [(x - cx_) * dx + (z - cz_) * dz for x, z in C]; p0, p1 = min(pr), max(pr)
                u = [(v - p0) / ((p1 - p0) or 1) for v in pr]; o, dirv, r0, r1, length = [cx_, cz_], [dx, dz], p0, p1, p1 - p0
        big = len(gids) >= 30
        dur = stagecraft.stage_duration(cam, t0, centre, length, float(st.get('dur', 0)), TIMING['min_stage'] if big else TIMING['min_stage_small'], TIMING['frames_per_s'])
        nz = float(st.get('noise', .12))
        for g, uu in zip(gids, u):
            h = random.Random(g * 7919 + 13).random(); start[g] = t0 + (uu * (1 - nz) + h * nz) * dur
        t1 = t0 + dur * (1 - nz)
        w = (r1 - r0) * TIMING['scan_w'] if mode == 'scan' else 0.0
        curve_ = [[round(t0, 3), round(r0 - (w if mode == 'scan' else 0), 6)], [round(t1, 3), round(r1 + (w if mode == 'scan' else 0), 6)]]
        if mode == 'ring':   # past the last building the ring runs on, gathering speed, until no part of it is on screen
            r_off = max(stagecraft.ring_exit(cam, t1 + k_, o, model_ground(*o), far_corner(o)) for k_ in (0.0, TIMING['ring_out'] / 2, TIMING['ring_out'])); v1 = (r1 - r0) / max(t1 - t0, 1e-3)
            if r_off > r1 * 1.01:
                T_ = TIMING['ring_out'] if r1 + v1 * TIMING['ring_out'] < r_off else (r_off - r1) / max(v1, 1e-6)
                acc = 2 * (r_off - r1 - v1 * T_) / (T_ * T_)
                curve_ += [[round(t1 + T_ * k / 8, 3), round(r1 + v1 * T_ * k / 8 + acc * (T_ * k / 8) ** 2 / 2, 6)] for k in range(1, 9)]
        fronts.append({'mode': mode, 'o': [round(o[0], 6), round(o[1], 6)], 'dir': [round(v, 6) for v in dirv] if dirv else None,
                       'curve': curve_,
                       'w': round(w, 6), 'a': [round(t0 - TIMING['fade'], 3), round(max(t1 + grow * .5, curve_[-1][0]), 3)], 'n': len(gids),
                       '_plan': {'t_from': t_from, 't0': t0, 't_end': round(t0 + dur + grow, 3), 'centre': centre, 'rad': rad_, 'n': len(gids),
                                 'focus': look_target(G, gids, cs, node_id, mode == 'scan')}})   # for plan_stages (popped)
    st_p = [start[gid] for gid, _, _ in meta]
    on = min(st_p); span = max(1e-3, max(st_p) - on)
    return on, span, [(v - on) / span for v in st_p], fronts, grow

def camv(k):
    """camera key: v = [tx, ty, tz, az, el, d] in model units, or ll = [lon, lat] (+ y, az, el, d) for a target on the map"""
    fov = k.get('fov', FM.get('fov', 30))   # a seventh value: wide lenses for the street-level glides
    if 'v' in k: return list(k['v'][:6]) + [fov]
    x, z = F.model_lonlat(*k['ll']); y = ground_ll(*k['ll']) + k.get('y', 0)
    return [round(x, 5), round(y, 5), round(z, 5), k['az'], k['el'], k['d'], fov]

# ------------------------------------------------------------------ layout: opening -> nodes -> closing
OP = FM.get('opening', {'dur': 5.0}); CL = FM.get('closing', {})
cursor = float(OP.get('dur', 5.0))
light = {'lightsOut': round(cursor - 1.2, 3), 'lamp': round(cursor, 3), 'darks': []}
yearline = []
nodes_out = []
epochs, lines, pins, marks, picks, ranges, readouts, cues, cam, decals_out, footage_out, grow, height, evs = [], [], [], [], [], [], [], [], [], [], [], None, None, []
props_out, tally_keys, sections, eras_out, hide_regions, night_keys, routes_out, dim_keys = [], [], [], [], [], [], [], []
ctx_keys = []   # the land beyond the plate (terrain.context): [t, [opacity]]
sky_out = None
def tour_subjects(node):
    """the points a tour stop must show (model xyz on the ground): its pins and the outlines of its named areas inside the plate"""
    pts = []
    for p in node.get('pins', []):
        if p.get('offscreen_ok'): continue
        x, z = pos_of(p)[:2]; pts.append((x, model_ground(x, z), z))
    for a_ in node.get('areas', []):
        if a_.get('frame') is False: continue
        for r in area_rings(a_['id']):
            q = [F.model_lonlat(lon, lat) for lon, lat in r]
            q = [(x, z) for x, z in q if abs(x) <= F.size[0] / 2 and abs(z) <= F.size[1] / 2]
            pts += [(x, model_ground(x, z), z) for x, z in q[::max(1, len(q) // 40)]]
    return pts

AREAS = None
def area_rings(aid):
    """the outer rings (lon/lat) of a researched area (film.areas_file, a GeoJSON with properties.id; research/*.md say where
    each came from and how sure it is), clipped to nothing: the plate's edge cuts what lies beyond"""
    global AREAS
    if AREAS is None:
        p_ = os.path.join(D, FM.get('areas_file', 'research/modern_areas.geojson'))
        AREAS = {f_['properties']['id']: f_ for f_ in json.load(open(p_, encoding='utf-8'))['features']} if os.path.exists(p_) else {}
    if aid not in AREAS: raise SystemExit(f'compile: area {aid!r} is not in {FM.get("areas_file", "research/modern_areas.geojson")}')
    g_ = AREAS[aid]['geometry']
    if g_['type'] == 'Point': return []   # (no boundary found: the research gives a representative point only, area_point)
    return [poly[0] for poly in (g_['coordinates'] if g_['type'] == 'MultiPolygon' else [g_['coordinates']])]

def area_point(aid):
    """an area with no boundary (status not found): its representative point (lon, lat), or None for one with a boundary"""
    area_rings(aid); g_ = AREAS[aid]['geometry']
    return g_['coordinates'] if g_['type'] == 'Point' else None

def expand_areas(node):
    """a node's `areas` (SKILL.md 演出文法 9k): each area the narration names is drawn as a lit outline in its own colour, with its
    name, and flashes when it is named (flash: node seconds, or {with: <line id>, plus: s}) -> the node's lines and pins.
    An area that follows a line (with: <line id>, plus: seconds after its start) hands that on: the outline starts then, its name
    `lead` seconds later and stays to the node's end, or to the end of that line (until: <line id>) plus hold seconds when either
    is given (bind_pictures)"""
    from shapely.geometry import Polygon as _Pg
    for a_ in node.get('areas', []):
        rings = area_rings(a_['id']); pt_ = area_point(a_['id'])
        if 'with' in a_ and 'at' in a_: raise SystemExit(f'compile: node {node["id"]}: area {a_["id"]} has with and at: one or the other')
        def at_(): return {'with': a_['with'], 'plus': float(a_.get('plus', 0))} if 'with' in a_ else {'at': a_.get('at', 0)}
        def name_(lead):   # (when its name shows)
            if 't0' in a_ or 'with' not in a_: return {'t0': a_.get('t0', a_.get('at', 0) + lead), 't1': a_.get('t1', 'end')}
            w_ = {'with': a_['with'], 'plus': float(a_.get('plus', 0)) + lead, **{k: a_[k] for k in ('until', 'hold', 't1') if k in a_}}
            return w_ if 'until' in a_ or 'hold' in a_ or 't1' in a_ else {**w_, 't1': 'end'}
        unseen_ = {'unseen_ok': True} if a_.get('unseen_ok') else {}   # (its name known never to be drawn, and accepted: readcheck)
        if pt_ is not None:   # no boundary: named at its point (a pin), never an invented outline
            node.setdefault('pins', []).append({'id': f'pa_{node["id"]}_{a_["id"]}', 'lon': pt_[0], 'lat': pt_[1], 'h_m': a_.get('h_m', 40), 'col': a_['col'],
                                                **name_(.3), **{l_: a_.get(l_) for l_ in LANG}, 'len': a_.get('len', 90), **unseen_})
            continue
        if a_.get('fill', .45) > 0:   # the buildings inside take the area's colour, the mask's edge glows: it reads in a dense city
            node.setdefault('epochs', []).append({'id': f'ar_{node["id"]}_{a_["id"]}', 'polygons': [[list(q) for q in r] for r in rings], **at_(),
                                                  'fade': a_.get('fade', 1.0), 'gain': a_.get('fill', .45), 'rim': a_.get('rim', 1.0), 'col': a_['col'], 'reach': 'fit',
                                                  'flash': a_.get('flash', []), **({'persist': True} if a_.get('persist') else {})})
        node.setdefault('lines', []).append({'id': f'area_{node["id"]}_{a_["id"]}', 'src': 'custom', 'col': a_['col'], 'width': a_.get('width', .0024), 'screen': True,
                                             **at_(), 'fade': a_.get('fade', 1.0), 'persist': a_.get('persist', False), 'gain': a_.get('gain', 1.0),
                                             'polylines': [list(r) + [r[0]] for r in rings], 'flash': a_.get('flash', [])})
        if any(a_.get(l_) for l_ in LANG):
            from shapely.geometry import box as _bx
            plate_ = _bx(*C['box'])   # (the part on the plate: a large area mostly beyond its edge is named where it can be seen)
            in_ = [q.intersection(plate_) for q in (_Pg(r).buffer(0) for r in rings)]; in_ = [q for q in in_ if not q.is_empty]
            ll_ = a_.get('label_ll') or (lambda q: [q.x, q.y])(max(in_ or [_Pg(rings[0])], key=lambda q: q.area).representative_point())
            node.setdefault('pins', []).append({'id': f'pa_{node["id"]}_{a_["id"]}', 'lon': ll_[0], 'lat': ll_[1], 'h_m': a_.get('h_m', 40), 'col': a_['col'],
                                                **name_(.5), **{l_: a_.get(l_) for l_ in LANG}, 'len': a_.get('len', 90), **unseen_})

PRIMS, IMPACT, FOLLOW, FOLLOW_KEYS = {}, {}, [], []
CITY_META = {}

def gen_city(node):
    """a whole period city, generated from its spec (pipeline/citygen.py) at the top of its node: the camera planning (a beam
    that lands on it, SKILL.md 演出文法 9c) needs where its buildings are"""
    cs = node['city']; xa = None
    if cs.get('avoid_eras'):   # quarters added on top of an earlier city that still stands: keep clear of its footprints
        import shapely as _sh
        fx = []
        for oid in cs['avoid_eras']:
            for p in PRIMS[oid]:
                if p[11] == 4: continue
                t_, cx, cz, rot = p[0], p[1], p[2], p[3]
                hw, hd = (max(p[5], p[8] if t_ == 2 else 0) / 2 + (p[8] if t_ == 1 else 0), max(p[6], p[9] if t_ == 2 else 0) / 2) if t_ in (0, 1, 2) else (p[5], p[5])
                c_, s_ = math.cos(rot), math.sin(rot)
                fx.append([((cx + x * c_ - z * s_) / F.scale + F.cx, -(cz + x * s_ + z * c_) / F.scale + F.cy) for x, z in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd))])
        xa = _sh.union_all(_sh.buffer(_sh.polygons(fx), 4.0, join_style='mitre'))
    meta_ = []; PRIMS[node['id']] = citygen.build_city(cs, F, ground_m_mesh, _tex, osm_rings, extra_avoid=xa, meta=meta_)
    CITY_META[node['id']] = meta_
CHANGE = None   # what grew taller where (ghsl_change), when a node asks for it   # era primitives by id; a node's landing beam; camera follow windows (hand keys must stay out)
PROP_MARKS = {}   # prop id -> [x, z, top_y] so pins can anchor on props
MW = 2048; MH = round(MW * F.size[1] / F.size[0])
mask_chans = []; MASK_USE = []   # epoch mask channels and what uses each (on, off, shape, wash disk)
def uoff_(u_):   # a mask's end in seconds once known (`until` a node: that node's end, once the loop has timed it)
    o_ = u_['off']
    return o_.get('_t1') if isinstance(o_, dict) else o_
PX = lambda ring: [(F.uv(*F.to_utm.transform(lon, lat))[0] * MW, F.uv(*F.to_utm.transform(lon, lat))[1] * MH) for lon, lat in ring]
bands = C['bands']
first_year = None

def node_time(node, v, default=None):
    """relative seconds / {year} / 'end' -> absolute seconds"""
    if v is None: return default
    if v == 'end': return node['_t1']
    if isinstance(v, (int, float)):   # seconds, stretched for the cues, plus the time inserted before them
        return round(node['_t0'] + float(v) * node.get('_k', 1.0) + sum(q['delta'] for q in node.get('_ins', []) if q['tau'] < float(v)), 3)
    if isinstance(v, dict) and 'with' in v:   # a picture that follows a line of its node: the line's start (edge: end, its end)
        lt_ = node.get('_line_t', {}).get(v['with'])
        if lt_ is None: raise SystemExit(f'compile: node {node.get("id")}: with: {v["with"]!r} is not a line of this node (script.yaml)')
        return round(lt_[1 if v.get('edge') == 'end' else 0] + float(v.get('plus', 0)), 3)
    if isinstance(v, dict) and 'abs' in v: return round(float(v['abs']), 3)
    if isinstance(v, dict) and 'year' in v:
        y0, y1 = node['_years']; t0, t1 = node['_t0'], node['_t1']
        if node.get('_tourA'): t1 = t0 + node['_tourA']   # a tour beat: the counter runs during the flight, then holds
        k = 0 if y1 == y0 else (float(v['year']) - y0) / (y1 - y0)
        return round(t0 + max(0, min(1, k)) * (t1 - t0) + float(v.get('plus', 0)), 3)
    raise ValueError(f'bad time {v!r} in node {node.get("id")}')

LINE_GAP = .35     # between one line's reading time and the next line
# the default kicker of a "today" picture: first language, the second in capitals, the first's word for footage (今天 · TODAY · 实拍)
KICKER_TODAY = ' · '.join([i18n.word(LANG[0], 'today')] + ([i18n.word(LANG[1], 'today').upper()] if len(LANG) > 1 else []) + [i18n.word(LANG[0], 'footage')])
LINE_FIRST = .5    # a node's first line, when it follows nothing: this long after the node arrives

def line_anchor(node, ln):
    """when a line that waits for a picture (`with`) may start: film seconds, and the node seconds of that picture (where time
    goes in if the words before it run long). with: shot:<camera key shot> | pin:<id> | card:<footage id> | stage[:<name>] |
    node (the node's arrival); lead: seconds before it"""
    w_ = str(ln['with']); kind_, _, name_ = w_.partition(':')
    if kind_ == 'node': tau_ = 0.0
    elif kind_ == 'shot':
        k_ = next((k for k in node.get('camera', []) if k.get('shot') == name_), None)
        if k_ is None: raise SystemExit(f'compile: line {ln["id"]}: no camera key with shot: {name_} in node {node["id"]}')
        tau_ = float(k_['t'])
    elif kind_ in ('pin', 'card', 'route'):
        L_ = {'pin': node.get('pins', []), 'card': node.get('footage', []), 'route': node.get('routes', [])}[kind_]
        it_ = next((q for q in L_ if q.get('id') == name_), None)
        if it_ is None: raise SystemExit(f'compile: line {ln["id"]}: no {kind_} {name_!r} in node {node["id"]}')
        tau_ = it_.get('t0' if kind_ == 'pin' else 'at', 0)
    elif kind_ == 'stage':
        st_ = (node.get('city') or {}).get('stages') or []
        it_ = next((q for q in st_ if not name_ or q.get('name') == name_), None)
        if it_ is None: raise SystemExit(f'compile: line {ln["id"]}: no stage {name_ or "(first)"} in node {node["id"]}')
        tau_ = it_.get('at', 0)
    else: raise SystemExit(f'compile: line {ln["id"]}: with: {w_!r} (shot:<name>, pin:<id>, card:<id>, route:<id>, stage[:<name>] or node)')
    if not isinstance(tau_, (int, float)): raise SystemExit(f'compile: line {ln["id"]}: {w_} has no time of its own to wait for (it follows a line itself?)')
    return node_time(node, float(tau_)) - float(ln.get('lead', 0)), float(tau_)

# the voice (design phase 4): once a line is recorded or generated, build/audio/voice/<language>/<line id>.wav (or .mp3, .m4a, .ogg),
# its length times the line instead of the reading estimate (film.voice: the voiced language, default the first); the pictures that
# follow the line move with it
VOICE_LANG = (FM.get('voice') or {}).get('lang', LANG[0])
VOICE_DIR = os.path.join(D, 'build', 'audio', 'voice', VOICE_LANG)
_VOICE = {}
def voice_len(lid):
    if lid in _VOICE: return _VOICE[lid]
    v_ = None
    for ext_ in ('wav', 'mp3', 'm4a', 'ogg', 'flac'):
        f_ = os.path.join(VOICE_DIR, f'{lid}.{ext_}')
        if not os.path.exists(f_): continue
        if ext_ == 'wav':
            import wave
            with wave.open(f_) as w_: v_ = w_.getnframes() / float(w_.getframerate())
        else:
            import subprocess
            v_ = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f_], capture_output=True, text=True).stdout.strip())
        break
    _VOICE[lid] = v_; return v_
VOICE_TAIL = .3   # after the voice ends, before the next line may start

def schedule_lines(node, dur):
    """when each line of a node is spoken (SKILL.md 演出文法 5c), film seconds -> node['_line_t'] {id: (start, end)},
    node['_pauses'] [(from, to)]. In the order of script.yaml:
      with: <picture>   waits for that picture (line_anchor); the picture waits for it in turn when the lines before run long
                        (time goes in just before the picture: kind 'words')
      t: <seconds>      the old way: that moment of the node's picture, moving with every insertion; the picture waits likewise
      neither           follows the line before (LINE_GAP after its reading time), through any hold the camera makes
      { pause: s }      a silence meant to be there (no check counts it as dead air)
    No line before the node's arrival; the node lasts until its last line has been read."""
    arrive_ = node_time(node, 0)   # (after a tour's flight or a beam's approach: inserted before the node's own second 0)
    for _it in range(80):
        prev_end, out_, pauses_, fix_ = arrive_, {}, [], None
        for ln in node.get('cues', []):
            if 'pause' in ln:
                pauses_.append((prev_end, prev_end + float(ln['pause']))); prev_end += float(ln['pause']); continue
            need_ = max(hold(ab(ln)[0]), hold(ab(ln)[1]), (voice_len(ln['id']) or 0) + VOICE_TAIL)   # (read, or heard)
            if 'with' in ln: early_, tau_ = line_anchor(node, ln)
            elif isinstance(ln.get('t'), (int, float)): early_, tau_ = node_time(node, float(ln['t'])), float(ln['t'])
            else: early_, tau_ = (prev_end if out_ else arrive_ + LINE_FIRST), None   # (a node's first line: a breath after it arrives)
            go_ = max(early_, prev_end, arrive_)
            if tau_ is not None and go_ > early_ + .05:   # the words before run long: the picture this line waits for waits too
                fix_ = (round(tau_ - 1e-3, 4), math.ceil((go_ - early_) * 100) / 100); break
            out_[ln['id']] = (round(go_, 3), round(go_ + need_, 3)); prev_end = go_ + need_ + LINE_GAP
        if fix_ is None:
            end_ = node['_t0'] + dur * node.get('_k', 1.0) + sum(q['delta'] for q in node['_ins'])
            if prev_end + .15 > end_ + .01: fix_ = (round(dur - 1e-3, 4), math.ceil((prev_end + .15 - end_) * 100) / 100)   # the last line: the node runs on
        if fix_ is None: break
        node['_ins'].append({'tau': fix_[0], 'delta': fix_[1], 'keys': [], 'kind': 'words', 'why': 'the lines before need the time'})
        node['_ins'].sort(key=lambda q: q['tau'])
    else: raise SystemExit(f'compile: node {node["id"]}: the lines did not settle')
    node['_line_t'], node['_pauses'] = out_, pauses_

def bind_pictures(node):
    """pictures that follow a line of their node (with: <line id>, plus: seconds after its start): a card, a route, a mask, a map
    line, a decal or a city's stage starts then; a pin or a terrain section shows from then until the end of that line (or of
    until: <line id>) plus hold seconds. An area hands its with on to the outline and name it becomes (expand_areas). The time
    itself is node_time's {with: ...}"""
    W_ = lambda it, plus: {'with': it['with'], 'plus': float(it.get('plus', plus))}
    for lst in (node.get('footage', []), node.get('routes', []), node.get('epochs', []), node.get('lines', []), node.get('decals', []),
                (node.get('city') or {}).get('stages', [])):
        for it in lst:
            if 'with' not in it: continue
            if isinstance(it.get('at'), (int, float)): raise SystemExit(f'compile: node {node["id"]}: {it.get("id", "a stage")} has with and at: one or the other')
            it['at'] = W_(it, 0.0)
    for p in node.get('pins', []) + node.get('sections', []):
        if 'with' not in p: continue
        p['t0'] = W_(p, .3)
        if 't1' not in p: p['t1'] = {'with': p.get('until', p['with']), 'edge': 'end', 'plus': float(p.get('hold', 1.5))}

LEAD_K = .15       # a beam-following camera aims this far along the beam ahead of its head
FOLLOW_LIFT = .5   # ... and lifts its aim by this share of the head's height above the ground (the arc stays in the picture)

def route_pts3(rt):
    """a light path: its lon/lat points in model [x, z, ground y] and the arc drawn through them in model xyz (each hop arcs
    up by `arc` x its length)"""
    ll = rt['pts'] if 'pts' in rt else [rt['from'], rt['to']]
    P3 = [F.model_lonlat(*q) + [ground_ll(*q)] for q in ll]
    pts3 = []
    for i, (a, b) in enumerate(zip(P3[:-1], P3[1:])):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = 8
        for j in range(n + (1 if i == len(P3) - 2 else 0)):
            k = j / n; pts3.append([a[0] + (b[0] - a[0]) * k, a[2] + (b[2] - a[2]) * k + rt.get('arc', .18) * L * 4 * k * (1 - k) + .003, a[1] + (b[1] - a[1]) * k])
    return P3, pts3

def path_at(pts, k):
    """the point at fraction k of a polyline's length (the beam's head: the engine draws it by length)"""
    L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + math.dist(a, b))
    d = min(1.0, max(0.0, k)) * L[-1]
    for i in range(len(pts) - 1):
        if d <= L[i + 1] or i == len(pts) - 2:
            f = min(1.0, max(0.0, (d - L[i]) / ((L[i + 1] - L[i]) or 1e-9))); return [pts[i][j] + (pts[i + 1][j] - pts[i][j]) * f for j in range(3)]
    return list(pts[-1])

def arrive_view(node, az_from, el, fov):
    """where the camera turns once a beam has landed on a city (SKILL.md 演出文法 9c): the node's own direction (its first
    camera key, else north up), the city's first stage (the one the beam lands on) whole in the picture, no nearer than the
    landing (a small town is seen with the land round it, where the colour ring goes)"""
    if node['id'] not in PRIMS: return None
    G, order = stage_parts(PRIMS[node['id']], CITY_META[node['id']], node['city'], node['id'])
    gids = next((g for _, first, g in order if first), None)
    if not gids: return None
    C = [G[g]['c'] for g in gids]
    hk = sorted([k for k in node.get('camera', []) if isinstance(k.get('t'), (int, float))], key=lambda k: k['t'])
    az = stagecraft.unwrap(camv(hk[0])[3] if hk else 0.0, az_from)
    x0, x1, z0, z1 = min(c[0] for c in C), max(c[0] for c in C), min(c[1] for c in C), max(c[1] for c in C)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    pts = [(x, model_ground(x, z), z) for x, z in C[::max(1, len(C) // 300)] + [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]]
    return [round(v, 6) for v in stagecraft.fit_distance([cx, model_ground(cx, cz), cz, az, el, 1.0, fov], pts, .88, .8)]

_FS = {}
def follow_shot(rt, node, cam_):
    """the camera that rides a beam (SKILL.md 演出文法 8, 9c): {keys: [[seconds from the launch, key]], end: seconds from the
    launch to the end of its window, v0: its first key, lead: seconds it starts before the launch}.
    Its direction is given (`follow.az`) or chosen: of behind the beam, behind at 25/45/65 degrees to either side and the two
    sides, the one nearest the way the camera faces now that keeps the origin in the picture at the launch, the head all the
    way (the aim follows the head and rises with the arc) and the landing point when it lands. A given direction must pass the
    same test. A beam that lands on a city (impact) then turns the camera to the city (arrive_view): the city grows from there."""
    ref = max(cam_, key=lambda k: k[0])[1][3] if cam_ else 0.0
    ck = (rt['id'], round(ref, 3))
    if ck in _FS: return _FS[ck]
    fo = rt['follow'] if isinstance(rt['follow'], dict) else {}
    P3, pts3 = route_pts3(rt)
    tot2 = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(P3[:-1], P3[1:]))
    draw, lead, hold = float(rt.get('draw', 2.5)), float(fo.get('lead', 1.2)), float(fo.get('hold', 2.4))
    el, fov = float(fo.get('el', 38)), fo.get('fov', FM.get('fov', 30))
    d = float(fo.get('d', max(.35, min(1.6, tot2 * .9)))); d_land = float(fo.get('land_d', d * .7))
    ss_ = lambda x: (lambda c: c * c * (3 - 2 * c))(min(1, max(0, x)))
    ahead = lambda k_: k_ + LEAD_K * (1 - k_)   # the camera looks a little ahead of the head: the origin and where it goes, both
    def aim(k_):
        x, y, z = path_at(pts3, k_); g = model_ground(x, z); return [x, g + FOLLOW_LIFT * max(0.0, y - g), z]
    n_ = max(3, int(draw / .4))
    def flight(az):
        ks = [[-lead, aim(ahead(0)) + [az, el, d, fov]]]
        for j in range(n_ + 1):
            s_ = ss_(j / n_); ks.append([round(draw * j / n_, 4), aim(ahead(s_)) + [az, el, d + (d_land - d) * s_, fov]])
        return ks
    def margin(ks):   # how far inside the frame the worst of origin (launch), head (flight) and landing stays; < 0: out
        C_ = stagecraft.Camera(ks, fov)
        def m(t, X):
            q = C_.project(t, X); return -1.0 if q is None else min(.9 - abs(q[0]), .85 - abs(q[1]))
        w = min(m(0.0, pts3[0]), m(draw, pts3[-1])); t = 0.0
        while t <= draw + 1e-6: w = min(w, m(t, path_at(pts3, ss_(t / draw)))); t += .1
        return w
    (sx, _, sz), (ex, _, ez) = pts3[0], pts3[-1]; dirz = math.degrees(math.atan2(ex - sx, ez - sz))   # the way the beam goes
    cands = [stagecraft.unwrap(float(fo['az']), ref)] if 'az' in fo else [stagecraft.unwrap(dirz + r, ref) for r in (180, 155, -155, 135, -135, 115, -115, 90, -90)]
    scored = [(az, margin(flight(az))) for az in cands]; ok = [c for c in scored if c[1] >= 0]
    if ok: az = min(ok, key=lambda c: abs(c[0] - ref))[0]
    elif 'az' in fo: raise SystemExit(f'compile: route {rt["id"]}: follow az {fo["az"]} loses the beam ({scored[0][1]:+.2f} of the frame): leave az out or give another')
    else:
        az = max(scored, key=lambda c: c[1])[0]
        print(f'  route {rt["id"]}: no follow direction keeps the whole beam in the picture; the best loses {-max(c[1] for c in scored):.2f} of the frame')
    keys = flight(az); land = keys[-1][1]
    E = arrive_view(node, az, el, fov) if rt.get('impact') and 'city' in node else None
    if E is not None:   # a moment on the landing (the flash), then the paced turn to the city
        E[5] = max(E[5], d_land)
        end = draw + .6 + stagecraft.move_time(land, E, speed=.6)
        keys += [[round(draw + .6, 4), land[:3] + [az + 2, el, d_land, fov]], [round(end, 4), E]]
    else:
        end = draw + hold; keys.append([round(end, 4), land[:3] + [az + 4, el + 2, d_land, fov]])
    _FS[ck] = {'keys': keys, 'end': round(end, 3), 'v0': keys[0][1], 'lead': lead, 'az': az, 'scored': scored}
    return _FS[ck]

def node_rel(node, t):
    """absolute seconds -> node seconds (inside inserted time: where it was inserted)"""
    acc, k = 0.0, node.get('_k', 1.0)
    for q in node.get('_ins', []):
        b_ = node['_t0'] + q['tau'] * k + acc
        if t <= b_: break
        if t <= b_ + q['delta']: return q['tau']
        acc += q['delta']
    return (t - node['_t0'] - acc) / k

for i, node in enumerate(FM['nodes']):
    if 'city' in node: gen_city(node)
    expand_areas(node)
    if node.get('dark'):   # a silence before the node: projector off
        light['darks'].append([round(cursor, 3), round(cursor + float(node['dark']), 3)]); cursor += float(node['dark'])
    cursor += float(node.get('gap', 0))
    dur = float(node['dur'])
    k_ = 1.0   # (no longer stretched as a whole for its words: schedule_lines inserts time only where a line needs it)
    node['_k'] = k_; node['_ins'] = sorted(PLAN.get(node['id'], []), key=lambda q: q['tau'])   # stable: same tau keeps the order found
    node['_t0'] = round(cursor, 3)
    for rt in node.get('routes', []):   # a beam the camera follows leaves only once the camera is behind its origin, in the time
        if not rt.get('follow') or not cam: continue   # the move needs (no cut): time inserted before the launch
        prev_ = max(cam, key=lambda k: k[0]); fs_ = follow_shot(rt, node, cam); v0_, lead_ = fs_['v0'], fs_['lead']
        A_ = stagecraft.move_time(prev_[1], v0_, speed=.6); need_ = prev_[0] + A_ + lead_; at_ = float(rt.get('at', 0)); t_ = node_time(node, at_)
        if t_ < need_ - .05:
            node['_ins'].append({'tau': round(at_ - 1e-3, 4), 'delta': round(need_ - t_, 2), 'keys': [], 'kind': 'approach', 'why': f'the camera needs {A_:.1f} s to get behind the origin of {rt["id"]}'})
            node['_ins'].sort(key=lambda q: q['tau']); print(f'  route {rt["id"]}: launches {need_ - t_:.1f} s later: the camera needs {A_:.1f} s to get behind its origin')
    if node.get('tour') and cam:   # a beat of a tour (SKILL.md 演出文法 9i): the camera flies here from the last beat while the
        TC = {'rate': 1.0, 'fly_spin': 5.0, 'spin': 1.0, 'push': .08, **FM.get('tour', {})}   # counter runs (at most `rate` years a second), then holds
        tr_ = node['tour']; prev_ = max(cam, key=lambda k: k[0]); pv_ = list(prev_[1])
        ys_ = node.get('years') or [node['year'], node['year']]
        tx_, tz_ = F.model_lonlat(*tr_['ll']); fov_ = tr_.get('fov', FM.get('fov', 30))
        V1 = [tx_, model_ground(tx_, tz_), tz_, pv_[3], float(tr_.get('el', 36)), float(tr_['d']), fov_]
        subj_ = tour_subjects(node)   # what the stop talks about (its pins, its named areas): the arrival view frames them all
        for _ in range(2):   # (the flight's length turns the camera, the turn changes the framing: twice settles it)
            A_ = max(1.3 * stagecraft.move_time(pv_, V1, speed=.8, t_max=9), (float(ys_[1]) - float(ys_[0])) / TC['rate'], 2.0)   # x1.3: eased in and out
            V1[3] = pv_[3] + float(tr_.get('fly_spin', TC['fly_spin'])) * A_   # the camera keeps turning round the city as it flies
            if 'az' in tr_: V1[3] = stagecraft.unwrap(float(tr_['az']), pv_[3])   # (or turns to a side that suits the place: the plate's edge behind it)
            if subj_:   # framed from the side that frames them closest (within 60 degrees of where the flight turns the camera to)
                xs_, zs_ = [q[0] for q in subj_], [q[2] for q in subj_]; cx_, cz_ = (min(xs_) + max(xs_)) / 2, (min(zs_) + max(zs_)) / 2
                azs_ = [V1[3]] if 'az' in tr_ else [V1[3] + o_ for o_ in (0, -20, 20, -40, 40, -60, 60)]
                fits_ = [stagecraft.fit_distance([cx_, model_ground(cx_, cz_), cz_, a_, V1[4], .1, fov_], subj_, .72, .62, d_lo=float(tr_.get('d_min', min(.35, float(tr_['d']))))) for a_ in azs_]   # (one subject: no nearer than the stop's own d or 3.5 km)
                V1 = min(fits_, key=lambda v_: (round(v_[5], 2), abs(v_[3] - azs_[0])))
                V1[5] = min(V1[5], float(tr_.get('d_max', 3.2)))
                # ... and still frames them at the end of the stay (the camera keeps turning and pushes in a little), clear of the subtitles
                for _k in range(40):
                    Ve_ = list(V1); Ve_[3] = V1[3] + float(tr_.get('spin', TC['spin'])) * float(node['dur']); Ve_[5] = V1[5] * (1 - TC['push'])
                    if V1[5] >= float(tr_.get('d_max', 3.2)) or (stagecraft.in_frame(V1, subj_, .74, .6) and stagecraft.in_frame(Ve_, subj_, .74, .6)): break
                    V1[5] *= 1.05
        dist_ = math.dist(pv_[:3], V1[:3]); lift_ = min(1.2, dist_ / max(pv_[5] + V1[5], 1e-3))   # a far hop goes up and over
        n_ = max(2, int(A_ / 1.5)); fk_ = []
        for j in range(1, n_):   # (the beat's own first key is the arrival)
            f_ = j / n_; e_ = f_ * f_ * (3 - 2 * f_)
            v_ = [pv_[q] + (V1[q] - pv_[q]) * e_ for q in (0, 1, 2)] + [pv_[3] + (V1[3] - pv_[3]) * f_, pv_[4] + (V1[4] - pv_[4]) * e_,
                  math.exp(math.log(pv_[5]) + (math.log(V1[5]) - math.log(pv_[5])) * e_) * (1 + lift_ * 4 * f_ * (1 - f_)), fov_]
            fk_.append([round(A_ * f_, 3), {'v': [round(x, 6) for x in v_[:6]], 'fov': fov_}])
        node['_ins'].append({'tau': -1e-3, 'delta': round(A_, 2), 'keys': fk_, 'kind': 'tour', 'why': f'the flight to {node["id"]}'})
        node['_ins'].sort(key=lambda q: q['tau']); node['_tourA'] = round(A_, 2)
        node['_subj'] = subj_ + [tuple(V1[:3])]   # (its place names stay up through the stop: labels_out keep)
        Vend = list(V1); Vend[3] = V1[3] + float(tr_.get('spin', TC['spin'])) * float(node['dur']); Vend[5] = V1[5] * (1 - TC['push'])
        node['camera'] = [{'t': 0, 'v': V1[:6], 'fov': fov_}, {'t': float(node['dur']), 'v': Vend[:6], 'fov': fov_}]
    # every camera key (hand-set or inserted) must leave the camera the time its move needs (no jumps): time inserted after the
    # key before it (SKILL.md 演出文法 F)
    hk_ = [k for k in node.get('camera', []) if isinstance(k.get('t'), (int, float))]
    prev_ = max(cam, key=lambda k: k[0]) if cam else None
    import bisect
    for it_ in range(60):   # each entry: (time, key, where a pace insertion after it goes in node['_ins'], its tau)
        taus_ = [q['tau'] for q in node['_ins']]
        fw_ = [(node_time(node, r_.get('at', 0)) - follow_shot(r_, node, cam)['lead'] - .05, node_time(node, r_.get('at', 0)) + follow_shot(r_, node, cam)['end'] + .05)
               for r_ in node.get('routes', []) if r_.get('follow')]   # (a hand key inside a beam follow goes: the follow owns its window)
        seq_ = [(node_time(node, k['t']), camv(k), bisect.bisect_right(taus_, float(k['t']) + 1e-3), float(k['t']) + 1e-3, None) for k in hk_
                if not any(w0 <= node_time(node, k['t']) <= w1 for w0, w1 in fw_)]
        for qi_, q in enumerate(node['_ins']):
            at_ = node_time(node, q['tau']) + sum(o['delta'] for o in node['_ins'][:qi_] if o['tau'] == q['tau'])
            seq_ += [(at_ + off_, camv(kv_), qi_ + 1, q['tau'], qi_ if q['kind'] == 'tour' else None) for off_, kv_ in q['keys']]
        for rt in node.get('routes', []):   # a beam follow ends on the view it turns to after the landing: the next key must leave it time too
            if not rt.get('follow'): continue
            fs_ = follow_shot(rt, node, cam); te_ = node_time(node, rt.get('at', 0)) + fs_['end']
            tau_e = node_rel(node, te_) + 1e-3
            seq_.append((te_, list(fs_['keys'][-1][1]), bisect.bisect_right(taus_, tau_e), tau_e, None))
        seq_.sort(key=lambda x: x[0])
        if prev_ is not None:
            t0k_ = (min(k['t'] for k in hk_) - 1e-3) if hk_ else 0.0
            seq_ = [(prev_[0], list(prev_[1]), bisect.bisect_right(taus_, t0k_), t0k_, 'prev')] + seq_
        fix_ = None
        for (ta, va, posa, taua, ga), (tb, vb, _, _, gb) in zip(seq_, seq_[1:]):
            if gb is not None and (ga == gb or ga == 'prev'): continue   # inside a planned flight, or its start (its own pacing)
            vb = list(vb); vb[3] = stagecraft.unwrap(vb[3], va[3])
            if max(abs(x_ - y_) for x_, y_ in zip(va, vb)) < 1e-6: continue   # (no move: a hold, however short)
            need_ = stagecraft.move_time(va, vb, speed=.6, t_min=.8)
            if tb - ta < need_ - .05: fix_ = (posa, taua, round(need_ - (tb - ta), 2)); break
        if fix_ is None: break
        node['_ins'].insert(fix_[0], {'tau': round(fix_[1], 4), 'delta': fix_[2], 'keys': [], 'kind': 'pace', 'why': 'a camera move needs more time'})
    else: raise SystemExit(f'compile: node {node["id"]}: camera pacing did not settle')
    if os.environ.get('CT_PACEDBG'):
        for q in node['_ins']:
            if q['kind'] in ('pace', 'approach'): print(f'    {node["id"]}: {q["kind"]} +{q["delta"]:.2f} s at {q["tau"]:.2f}')
    schedule_lines(node, dur); bind_pictures(node)
    dur = dur * k_ + sum(q['delta'] for q in node['_ins'])
    node['_t0'] = round(cursor, 3); node['_t1'] = round(cursor + dur, 3)
    ys = node.get('years') or [node['year'], node['year']]; node['_years'] = [float(ys[0]), float(ys[1])]
    if first_year is None: first_year = node['_years'][0]
    if node.get('_tourA'): yearline += [[node['_t0'], node['_years'][0]], [round(node['_t0'] + node['_tourA'], 3), node['_years'][1]], [node['_t1'], node['_years'][1]]]
    else: yearline += [[node['_t0'], node['_years'][0]], [node['_t1'], node['_years'][1]]]
    T = lambda v, d=None, _n=node: node_time(_n, v, d)
    # the node's colour reaches today's city as a ring of light spreading from where the story just was: `wave_from` [lon, lat],
    # else the previous node's period city, else where the camera last looked
    prev = FM['nodes'][i - 1] if i else None
    if 'wave_from' in node: wv = F.model_lonlat(*node['wave_from'])
    elif prev is not None and 'city' in prev: wv = F.model_lonlat(*prev['city']['origin'])
    else:
        lk = (prev.get('camera') if prev is not None else OP.get('camera')) or [{'ll': FM['nodes'][0].get('camera', [{}])[0].get('ll', [0, 0])}]
        if prev is not None and not prev.get('camera') and prev.get('follow_change', {}).get('end'): lk = [prev['follow_change']['end']]
        k_ = lk[-1]; wv = F.model_lonlat(*k_['ll']) if 'll' in k_ else [k_['v'][0], k_['v'][2]]
    nodes_out.append({'id': node['id'], 't0': node['_t0'], 't1': node['_t1'], 'years': node['_years'], 'label': ab(node.get('label', {}))[0] or node['id'], 'label2': ab(node.get('label', {}))[1],
                      'col': node.get('col', '#ffffff'), 'tint': node.get('tint', FM.get('node_tint', .5)), 'wave': [round(wv[0], 5), round(wv[1], 5)],
                      'reset': float(node['reset']['year']) if 'reset' in node else None, 'ink': float(node.get('ink', 0)), 'era_tint': float(node.get('era_tint', node.get('tint', FM.get('node_tint', .5)))),
                      'arrive': round(node['_t0'] + node.get('_tourA', 0), 3), 'ghost': node.get('ghost', []), 'mood': node['_mood']})   # ghost: earlier cities whose outline is drawn again while this node is told   # today's city takes this colour while the node is told
    # readout (left column); a node without `readout: false` gets one with the year counter
    r = node.get('readout', {})
    if r is not False:
        d = {'id': 'r_' + node['id'], 't0': T(r.get('t0', 0.4)), 't1': T(r.get('t1', 'end')) - .2, 'idx': f'{len(readouts) + 1:02d}', 'name': pick(r.get('name')) or ab(node.get('label', {}))[0] or node['id'],
             'big': r.get('big', {'year': True}) if isinstance(r.get('big', {'year': True}), dict) else tx(str(r['big'])), 'unit': tx(r.get('unit')), 'col': r.get('col', node.get('col', '#ffffff')),
             'label': pick(r.get('label')), 'note': pick(r.get('note'))}
        if r.get('legendBands'): d['legendBands'] = r['legendBands'] if isinstance(r['legendBands'], dict) else {}
        if 'legend' in r: d['legend'] = [{'col': q.get('col'), 'text': tx(q.get('text')), 'text2': tx(q.get('text2'))} for q in r['legend']]
        if 'bar' in r: d['bar'] = {'cols': r['bar']['cols'], 'l0': pick(r['bar']['l0']), 'l1': pick(r['bar']['l1'])}
        readouts.append(d)
    for pr in node.get('props', []):       # schematic 3D models: positions lon/lat -> model units; dimensions in metres
        q = {k: v for k, v in pr.items() if k not in ('lon', 'lat', 'from', 'to', 'pts', 'at', 'off_at', 'until', 'persist', 'gates')}
        if 'lon' in pr: q['pos'] = F.model_lonlat(pr['lon'], pr['lat'])
        if 'from' in pr: q['from'] = F.model_lonlat(*pr['from']); q['to'] = F.model_lonlat(*pr['to'])
        if 'pts' in pr: q['pts'] = [F.model_lonlat(lon, lat) for lon, lat in pr['pts']]
        if 'osm' in pr: q['pts'] = [F.model_lonlat(lon, lat) for lon, lat in osm_rings(pr['osm'])[0]]
        if 'gates' in pr: q['gates'] = pr['gates']
        q['year'] = pr.get('year', node['_years'][0])
        q['on'] = T(pr.get('at', 0)); q['fade'] = pr.get('fade', 1.5); q['offStyle'] = pr.get('offStyle', 'fade'); q['offDur'] = pr.get('offDur', 1.2)
        q['off'] = T(pr.get('off_at')) if 'off_at' in pr else (None if pr.get('persist') else T('end'))
        if 'until' in pr: q['off'] = next(x for x in FM['nodes'] if x['id'] == pr['until'])
        props_out.append(q)
        if 'lon' in pr: PROP_MARKS[pr['id']] = q['pos'] + [round(ground_ll(pr['lon'], pr['lat']) + (pr.get('h_m', 10) + (pr.get('hall', {}).get('h_m', 0) if isinstance(pr.get('hall'), dict) else 0)) * F.scale, 6)]
        elif 'from' in pr:
            mid = [(pr['from'][0] + pr['to'][0]) / 2, (pr['from'][1] + pr['to'][1]) / 2]
            PROP_MARKS[pr['id']] = F.model_lonlat(*mid) + [round(ground_ll(*mid) + pr.get('h_m', 6) * F.scale, 6)]
        elif 'pts' in q and q['pts']:
            PROP_MARKS[pr['id']] = [q['pts'][0][0], q['pts'][0][1], round(pr.get('h_m', 8) * F.scale, 6)]
    # epochs: masks on the plate (+ the buildings inside), dated parts by year range
    for e in node.get('epochs', []):
        from shapely.geometry import Point as _Pt, Polygon as _Pg
        from shapely.ops import unary_union
        im = Image.new('L', (MW, MH), 0); dl = ImageDraw.Draw(im); pts_all = []; parts_ = []   # (parts_: the mask's shape in model units)
        for ring in e.get('polygons', []): dl.polygon(PX(ring), fill=255); pts_all += ring; parts_.append(_Pg([F.model_lonlat(*q) for q in ring]).buffer(0))
        for name in e.get('osm_polygons', []):
            rings = osm_rings(name); assert rings, f'OSM polygon {name!r} not in the cache'
            for ring in rings: dl.polygon(PX(ring), fill=255); pts_all += ring; parts_.append(_Pg([F.model_lonlat(*q) for q in ring]).buffer(0))
        for c in e.get('circles', []):
            x, y = F.to_utm.transform(c[0], c[1]); u, v = F.uv(x, y); rr = c[2] / (F.x1 - F.x0) * MW
            dl.ellipse([u * MW - rr, v * MH - rr, u * MW + rr, v * MH + rr], fill=255); pts_all.append((c[0], c[1])); parts_.append(_Pt(*F.model_lonlat(c[0], c[1])).buffer(c[2] * F.scale))
        if 'centre' in e: cx, cz = F.model_lonlat(*e['centre'])
        elif pts_all: cx, cz = F.model_lonlat(sum(p[0] for p in pts_all) / len(pts_all), sum(p[1] for p in pts_all) / len(pts_all))
        else: cx = cz = None
        off = T(e.get('off_at')) if 'off_at' in e else (None if e.get('persist') else T('end'))
        if 'until' in e: off = next(x for x in FM['nodes'] if x['id'] == e['until'])  # resolved below
        on_ = T(e.get('at', 0)); reach_ = e.get('reach', 0.7)
        if e.get('reach') == 'fit' and pts_all:   # (an area: the wash reaches just past its own outline)
            reach_ = round(max(math.hypot(F.model_lonlat(*q)[0] - cx, F.model_lonlat(*q)[1] - cz) for q in pts_all) * 1.08 + .01, 4)
        # eight mask channels for the whole film: a mask shares a channel with masks that are over before it starts and lie
        # outside the reach of its wash (its wash would light them too), else takes a new one
        shape_ = unary_union(parts_).buffer(.01) if parts_ else None
        disk_ = _Pt(cx, cz).buffer(reach_ if isinstance(reach_, (int, float)) else 9) if cx is not None else None
        idx = None
        off_n = off if isinstance(off, (int, float)) else (1e9 if off is None else None)   # (a mask to the end can still take a channel others have left)
        if off_n is not None and disk_ is not None:   # (a mask with no shape, dated parts only, puts no pixels in the channel)
            for ci_, ch_ in enumerate(MASK_USE):
                if all(isinstance(uoff_(u_), (int, float)) and u_['disk'] is not None and (uoff_(u_) < on_ - .3 or u_['on'] > off_n + .3)
                       and not (shape_ is not None and u_['disk'].intersects(shape_)) and not (u_['shape'] is not None and disk_.intersects(u_['shape'])) for u_ in ch_):
                    idx = ci_; break
        blur_ = im.filter(ImageFilter.GaussianBlur(e.get('soft_px', 2.5)))
        if idx is None:
            idx = len(mask_chans)
            if idx >= 12: print('   mask channels:', [[(u_['id'], u_['on'], uoff_(u_)) for u_ in ch_] for ch_ in MASK_USE], 'wanted by', e['id'], on_, off)
            assert idx < 12, 'at most 12 epoch mask channels in a film (masks that do not overlap in time and place share one)'
            mask_chans.append(blur_); MASK_USE.append([])
        else: mask_chans[idx] = ImageChops.lighter(mask_chans[idx], blur_)
        MASK_USE[idx].append({'id': e['id'], 'on': on_, 'off': off, 'shape': shape_, 'disk': disk_})   # (off: seconds, None = to the end, or the node it lasts until)
        ep = {'i': idx, 'id': e['id'], 'on': T(e.get('at', 0)), 'fade': e.get('fade', 1.5), 'off': off, 'offStyle': e.get('offStyle', 'fade'), 'offDur': e.get('offDur', 1.2),
              'yr': e.get('yr'), 'bld': 0 if e.get('buildings_inside') is False else 1, 'gain': e.get('gain', 1.0), 'rim': e.get('rim', 1.0), 'col': e.get('col')}
        if 'dimAt' in e: ep['dimAt'] = T(e['dimAt']); ep['dimTo'] = e.get('dimTo', .4)
        if cx is not None: ep['centre'] = [round(cx, 5), round(cz, 5)]; ep['reach'] = reach_
        if e.get('flash'): ep['flash'] = [T(v) for v in e['flash']]
        epochs.append(ep)
    for L in node.get('lines', []):
        d = {'id': L['id'], 'src': L.get('src', 'custom'), 'col': L['col'], 'width': L.get('width', .0015), 'on': T(L.get('at', 0)), 'fade': L.get('fade', 1.0),
             'off': T(L.get('off_at')) if 'off_at' in L else (None if L.get('persist', True) else T('end')), 'offStyle': 'fade', 'offDur': L.get('offDur', 1.0), 'gain': L.get('gain', 1)}
        if 'filter' in L: d['filter'] = L['filter']
        if 'flow' in L: d['flow'] = L['flow']
        if L.get('flash'): d['flash'] = [T(v) for v in L['flash']]   # moments it flares (an area as it is named)
        if L.get('screen'): d['screen'] = True   # keeps its width on screen in a wide shot (an area's outline)
        if d['src'] == 'custom': d['pts'] = [[F.model_lonlat(lon, lat) for lon, lat in pl] for pl in L['polylines']]
        lines.append(d)
    if 'grow' in node:
        G = node['grow']
        # the growth runs on the film's year counter, across the nodes that follow: a {year} is placed on the whole year line (below)
        grow = {'on': T(G.get('at', 0)), 'mono': bool(G.get('mono', False)), 'warm': float(G.get('warm', 0)), 'bands': [{'band': k, 't': T(b['t']), '_traw': b['t'], 'spread': b.get('spread', 1.0)} for k, b in enumerate(G['bands'])]}
        if 'dim' in G: grow['dim'] = {'t': T(G['dim']['t']), '_traw': G['dim']['t'], 'to': G['dim'].get('to', .4)}
        assert len(grow['bands']) == len(bands), 'grow.bands must list one entry per band'
        if G.get('change') == 'ghsl':   # what grew taller where (GHSL built-up volume, pipeline/ghsl_change.py); counters per year
            import ghsl_change
            CHANGE = ghsl_change.change(local.raw(), F, _MODEL, cache=LAYOUT.data(D, 'ghsl_change.json'))
            grow['counters'] = {'t0': T(G.get('counters_at', 1.0)), 't1': node['_t1'], '_until': G.get('counters_until'), 'a': [i18n.word(LANG[0], 'new'), i18n.word(LANG[0], 'taller')], 'b': [i18n.word(LANG[-1], 'new'), i18n.word(LANG[-1], 'taller')] if len(LANG) > 1 else None, 'note': tx(G.get('counters_note', 'GHSL 建成体积 · 100 m · 5 年 · 估算'))}
        if 'follow_change' in node:   # the camera flies over where the city changed most, window by window (SKILL.md 演出文法)
            fc = node['follow_change']; y0_, y1_ = node['_years']; K = int(fc.get('windows', 5))
            Mb = _MODEL['b']; ev = []   # (year, x, z, weight)
            from shapely.geometry import Polygon as _Pg, Point as _Pt
            reg_ = _Pg([F.model_lonlat(*q) for q in fc['region']]) if fc.get('region') else None   # only the changes in the film's subject
            for i_, rec in enumerate(_MODEL['p']):
                yr_ = Mb[rec[0]][0]; ring = rec[2][0]; x_ = sum(p[0] for p in ring) / len(ring); z_ = sum(p[1] for p in ring) / len(ring)
                if yr_ and y0_ < yr_ <= y1_ and (reg_ is None or reg_.contains(_Pt(x_, z_))): ev.append((yr_, x_, z_, rec[1]))
            for i_, f0_, yA_, yB_ in (CHANGE or {}).get('renew', []):
                ring = _MODEL['p'][i_][2][0]; x_ = sum(p[0] for p in ring) / len(ring); z_ = sum(p[1] for p in ring) / len(ring)
                if reg_ is None or reg_.contains(_Pt(x_, z_)): ev.append(((yA_ + yB_) / 2, x_, z_, _MODEL['p'][i_][1] * (1 - f0_)))
            ty = lambda Y: node['_t0'] + (Y - y0_) / ((y1_ - y0_) or 1) * (node['_t1'] - node['_t0'])
            az_ = float(fc.get('az0', 50)); daz = float(fc.get('az_step', -10))
            for k_ in range(K):
                a_, b_ = y0_ + (y1_ - y0_) * k_ / K, y0_ + (y1_ - y0_) * (k_ + 1) / K
                sel = [q for q in ev if a_ < q[0] <= b_ + 2]
                if not sel: continue
                cell_ = float(fc.get('cell_m', 900)) * F.scale; bins = {}   # the densest change in the window (not the average: that sits still)
                for q in sel: bins.setdefault((int(q[1] // cell_), int(q[2] // cell_)), []).append(q)
                best = max(bins.values(), key=lambda L: sum(q[3] for q in L)); W_ = sum(q[3] for q in best)
                cx_ = sum(q[1] * q[3] for q in best) / W_; cz_ = sum(q[2] * q[3] for q in best) / W_
                cam.append([round(ty((a_ + b_) / 2), 3), [round(cx_, 5), round(model_ground(cx_, cz_), 5), round(cz_, 5), round(az_ + daz * k_, 1), float(fc.get('el', 42)), float(fc.get('d', .65)), fc.get('fov', FM.get('fov', 30))]])
            if fc.get('end'):
                E_ = fc['end']; ex_, ez_ = F.model_lonlat(*E_['ll'])
                cam.append([node['_t1'], [round(ex_, 5), round(model_ground(ex_, ez_), 5), round(ez_, 5), float(E_.get('az', 0)), float(E_.get('el', 60)), float(E_.get('d', 2.2)), FM.get('fov', 30)]])
    if 'height' in node:
        Hh = node['height']; top = ST['tallest'][0]
        height = {'t0': T(Hh.get('t0', 0)), 't1': T(Hh.get('t1', 'end')), 'off': T(Hh.get('off_at')) if 'off_at' in Hh else None, 'top': top['pos'][2], 'topPos': [top['pos'][0], top['pos'][1]], 'max_m': top['h']}
    for p in node.get('picks', []):
        picks.append({'id': p['id'], 'pos': pos_of(p)[:2], 'r': p.get('r', .02), 'on': T(p.get('at', 0)), 'fade': p.get('fade', .6), 'off': T(p.get('off_at', 'end')), 'offStyle': 'fade', 'offDur': p.get('offDur', .8)})
    for p in node.get('pins', []):
        a, b = ab(p); sub = b if b else tx(p.get('sub'))
        t0 = T(p.get('t0', 0.6)); t1 = T(p.get('t1', 'end')); need = max(hold(a), hold(sub)) + 1.0
        if t1 < t0 + need: t1 = round(t0 + need, 3)
        pins.append({'id': p['id'], 'pos': pos_of(p), 't0': t0, 't1': t1, 'text': a, 'sub': sub, 'col': p.get('col', node.get('col')), 'dx': p.get('dx', 0), 'len': p.get('len', 110), 'left': p.get('left'),
                     '_node': node['id'], '_tour': bool(node.get('tour')), '_offok': bool(p.get('offscreen_ok')),
                     **({'unseen_ok': True} if p.get('unseen_ok') else {})})   # (never drawn, and the user accepts it: readcheck lets it pass)
    for m in node.get('marks', []):
        marks.append({'id': m['id'], 'pos': pos_of(m), 't0': T(m.get('t0', 0)), 't1': T(m.get('t1', 'end')), 'col': m.get('col', node.get('col')), 'r': m.get('r', 10), 'k': m.get('k', 0)})
    for rg in node.get('ranges', []):
        p0, p1 = pos_of(rg['from']), pos_of(rg['to']); nseg = 60
        pts = [[p0[0] + (p1[0] - p0[0]) * k / nseg, p0[1] + (p1[1] - p0[1]) * k / nseg] for k in range(nseg + 1)]
        len_m = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / F.scale; tick = rg.get('tick_m', 1000)
        ranges.append({'id': rg['id'], 'pts': pts, 't0': T(rg.get('t0', 0)), 't1': T(rg.get('t1', 2.5)), 'tOut': T(rg.get('tOut', 'end')), 'col': rg.get('col', '#ffffff'), 'len_m': round(len_m), 'ticks': [round(k * tick / len_m * nseg) for k in range(1, int(len_m / tick) + 1)]})
    if 'sky' in node:                      # a city laid out after the sky: asterisms drawn on their places, one by one (engine: overlay sky)
        sk = node['sky']; P3 = lambda x, y: F.model(x, y) + [round(ground_m_xy(x, y) * F.scale * _tex, 6)]
        LL = lambda lon, lat: P3(*F.to_utm.transform(lon, lat)); groups = []
        for gi, g in enumerate(sk['groups']):
            st, ln, band, lab = [], [], None, None; kind = g.get('kind', 'asterism')
            if kind == 'enclosure':        # 紫微垣-like: two walls of stars on an ellipse, open at both ends, a bright star inside
                cx, cy = F.to_utm.transform(*g['centre']); rx, ry = g['rx_m'], g['ry_m']; gap = math.radians(g.get('gap_deg', 30))
                for wall, (a0, a1, n) in enumerate(((-math.pi / 2 + gap, math.pi / 2 - gap, g['n'][0]), (math.pi / 2 + gap, 3 * math.pi / 2 - gap, g['n'][1]))):
                    for i in range(n):
                        an = a0 + (a1 - a0) * i / (n - 1); j = .07 * math.sin(i * 7.3 + wall * 2.1)
                        st.append(P3(cx + rx * (1 + j) * math.cos(an), cy + ry * (1 + j) * math.sin(an)) + [.55 + .35 * abs(math.sin(i * 3.1 + wall))])
                        if i: ln.append([len(st) - 2, len(st) - 1])
                if 'star' in g: st.append(LL(*g['star']) + [1.4])
                lab = P3(cx, cy + ry * 1.12)
            elif kind == 'asterism':       # stars at metre offsets (east, north) from a point; lines between them
                cx, cy = F.to_utm.transform(*g['at_ll'])
                for k_, (dx, dy) in enumerate(g['stars']): st.append(P3(cx + dx, cy + dy) + [.7 + .3 * ((k_ * 5) % 3) / 2])
                ln = [list(l) for l in g.get('lines', [])]
                lab = P3(cx, cy + max(dy for _, dy in g['stars']) + g.get('label_m', 350))
            elif kind == 'line':           # n stars along a line with a small zigzag (阁道 along the covered way)
                a_, b_ = F.to_utm.transform(*g['from']), F.to_utm.transform(*g['to']); n = g.get('n', 6); L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
                nx, ny = -(b_[1] - a_[1]) / L_, (b_[0] - a_[0]) / L_
                for i in range(n):
                    k_ = (i + .5) / n; o = g.get('jitter_m', 150) * (1 if i % 2 else -1)
                    st.append(P3(a_[0] + (b_[0] - a_[0]) * k_ + nx * o, a_[1] + (b_[1] - a_[1]) * k_ + ny * o) + [.75])
                    if i: ln.append([i - 1, i])
                lab = P3(a_[0] + (b_[0] - a_[0]) * g.get('label_at', .5) + nx * 600, a_[1] + (b_[1] - a_[1]) * g.get('label_at', .5) + ny * 600)
            elif kind == 'band':           # a river of stars along a polyline (天汉 along the Wei)
                pts = [F.to_utm.transform(lon, lat) for lon, lat in g['pts']]
                seglen = [math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts[:-1], pts[1:])]; tot = sum(seglen)
                def at_s(s_):   # point and left normal at a fraction of the polyline's length
                    d_ = s_ * tot
                    for i_, ((p, q), L_) in enumerate(zip(zip(pts[:-1], pts[1:]), seglen)):
                        if d_ <= L_ or i_ == len(seglen) - 1:
                            k_ = min(1, d_ / L_); return p[0] + (q[0] - p[0]) * k_, p[1] + (q[1] - p[1]) * k_, -(q[1] - p[1]) / L_, (q[0] - p[0]) / L_
                        d_ -= L_
                rnd = random.Random(gi + 11); parts = []
                for i in range(g.get('n', 1200)):
                    s_ = rnd.random(); x_, y_, nx, ny = at_s(s_); o = rnd.gauss(0, g.get('w_m', 900) / 2.6)
                    parts.append(P3(x_ + nx * o, y_ + ny * o) + [round(s_, 4), round(rnd.random() ** 3, 3)])
                band = {'parts': parts, 'line': [P3(*at_s(i / 60)[:2]) + [i / 60] for i in range(61)]}
                x_, y_, nx, ny = at_s(g.get('label_at', .5)); lab = P3(x_ + nx * 900, y_ + ny * 900)
            if 'label_ll' in g: lab = LL(*g['label_ll'])
            a_, b_ = ab(g)
            groups.append({'id': g['id'], 'on': T(g.get('at', 0)), 'draw': float(g.get('draw', 2.0)), 'stars': st, 'lines': ln, 'band': band, 'lab': lab, 'a': a_, 'b': b_})
        sky_out = {'on': T(sk.get('at', 0)), 'off': T(sk['off_at']) if 'off_at' in sk else node['_t1'], 'col': sk.get('col', '#cfe2ff'), 'scrim': sk.get('scrim', .58), 'groups': groups}
        node.setdefault('_owned', []).append((sky_out['on'], sky_out['off']))
    if 'dim_today' in node:                # today's city dims under something drawn on it (the finale's footprints)
        dt_ = node['dim_today']; dim_keys.extend([[T(dt_.get('at', 0)), [0.0]], [round(T(dt_.get('at', 0)) + 1.5, 3), [float(dt_.get('to', .5))]], [node['_t1'], [float(dt_.get('to', .5))]], [round(node['_t1'] + 1.5, 3), [0.0]]])
    if 'night' in node:                    # night state for this node (lit windows, flowing roads), eased in over 2.5 s
        night_keys.append([node['_t0'], night_keys[-1][1] if night_keys else [0.0]]); night_keys.append([round(node['_t0'] + 2.5, 3), [float(node['night'])]])
    elif night_keys and night_keys[-1][1][0] > 0:
        night_keys.append([node['_t0'], night_keys[-1][1]]); night_keys.append([round(node['_t0'] + 2.5, 3), [0.0]])
    if 'city' in node:                     # a whole period city (generated at the top of the node: gen_city)
        cs = node['city']; prims, meta_ = PRIMS[node['id']], CITY_META[node['id']]
        bnd = era_boundary(prims, cs)
        def at_of(v, _n=node):
            """an explicit era or stage start: node seconds or {after: route} (when the beam lands)"""
            if isinstance(v, dict) and 'after' in v:
                rt_ = next(r for r in _n.get('routes', []) if r['id'] == v['after'])
                return round(node_time(_n, rt_.get('at', 0)) + float(rt_.get('draw', 2.5)) + float(v.get('plus', .2)), 3)
            return node_time(_n, v)   # (not T: it is rebound for every node and this runs after the loop)
        fn = f'data/era_{node["id"]}.json'
        e = {'id': node['id'], 'file': fn, 'n': len(prims), 'col': cs.get('col', node.get('col', '#ffd9a0')), 'tint': cs.get('tint', .75),
             'sink': cs.get('sink', 3.0), 'sinkStyle': cs.get('sinkStyle', 'sink'),
             'fall': cs.get('fall', 'in' if cs.get('sinkStyle') == 'burn' else 'out'), 'fallDur': float(cs.get('fall_dur', TIMING['fall_dur'])),
             'off': T(cs['off_at']) if 'off_at' in cs else (None if cs.get('persist') else T('end'))}
        if 'until' in cs: e['off'] = ('t0', next(x for x in FM['nodes'] if x['id'] == cs['until']), float(cs.get('until_plus', 0)))
        if e['sinkStyle'] == 'burn': e['burn'] = cs.get('burn', 3.0)
        e['boundary'] = bnd
        e['outline'] = [[[round(x / F.size[0] + .5, 4), round(z / F.size[1] + .5, 4)] for x, z in r] for r in bnd]   # the locator's frame (plate uv)
        if 'reuse' in cs: e['reuse'] = cs['reuse']
        if len(hide_regions) < 8:   # where this era stands, today's buildings step aside (one channel per era; filled once the timing is known)
            e['hide'] = len(hide_regions); hide_regions.append(None); EDGES.append(None)
        e['_pend'] = {'cs': cs, 'node': node, 'prims': prims, 'meta': meta_, 'at_of': at_of, 'bnd': bnd}
        eras_out.append(e); print(f'  city {node["id"]}: {len(prims)} primitives')
    for rt in node.get('routes', []):      # a light path: a move, a shift, a distance (lon/lat points; each hop arcs up by `arc` x its length)
        ll = rt['pts'] if 'pts' in rt else [rt['from'], rt['to']]
        P3, pts3 = route_pts3(rt)
        km = sum(math.hypot(*(lambda u, v: (u[0] - v[0], u[1] - v[1]))(F.to_utm.transform(*u_), F.to_utm.transform(*v_))) for u_, v_ in zip(ll[:-1], ll[1:])) / 1000
        a_, b_ = ab(rt)
        fill = lambda s_: s_.replace('[km]', f'{km:.0f}' if km >= 10 else f'{km:.1f}') if s_ else s_
        lab = rt.get('label_at', .5); mid = pts3[min(len(pts3) - 1, int(lab * (len(pts3) - 1)))]
        on_r, draw_r = T(rt.get('at', 0)), float(rt.get('draw', 2.5))
        if rt.get('follow'):   # the camera rides the beam to where it lands, then turns to the city it lands on (follow_shot)
            fs_ = follow_shot(rt, node, cam); win = (on_r - fs_['lead'], on_r + fs_['end'])
            for tt, v in fs_['keys']:
                k_ = [round(on_r + tt, 3), [round(x, 6) for x in v[:6]] + [v[6]]]
                cam.append(k_); FOLLOW_KEYS.append(k_)
            FOLLOW.append((node['id'], rt['id'], win))
            print(f'  route {rt["id"]}: followed from az {fs_["az"]:.0f} (' + ', '.join(f'{a_:.0f}:{m_:+.2f}' for a_, m_ in fs_['scored']) + f'), the view turns to the city by {on_r + fs_["end"]:.1f} s')
        if rt.get('impact'):   # the beam lands on the node's city: its colour ring and the city's growth start there
            (sx_, sz_), (ex_, ez_) = P3[0][:2], P3[-1][:2]; L_ = math.hypot(ex_ - sx_, ez_ - sz_) or 1e-9
            IMPACT[node['id']] = {'route': rt['id'], 'land': round(on_r + draw_r, 3), 'end': [ex_, ez_], 'dir': [(ex_ - sx_) / L_, (ez_ - sz_) / L_], 'follow': bool(rt.get('follow')),
                                  'arrive': round(on_r + fs_['end'], 3) if rt.get('follow') else round(on_r + draw_r, 3)}
        routes_out.append({'id': rt['id'], 'pts': [[round(v, 5) for v in q] for q in pts3], 'col': rt.get('col', node.get('col', '#ffffff')), 'w': rt.get('w', .0011),
                           'on': on_r, 'draw': draw_r, 'impact': bool(rt.get('impact')), 'off': T(rt['off_at']) if 'off_at' in rt else round(on_r + float(rt.get('draw', 2.5)) + float(rt.get('hold', 3.5)), 3), 'a': fill(a_), 'b': fill(b_), 'lab': [mid[0], mid[2], mid[1]], 'km': round(km, 2)})
    for sc in node.get('sections', []):    # a terrain profile along a line (lon/lat endpoints), with labels at fractions of the line
        sections.append({'id': sc['id'], 'a': F.model_lonlat(*sc['from']), 'b': F.model_lonlat(*sc['to']), 't0': T(sc.get('t0', 0)), 't1': T(sc.get('t1', 'end')),
                         'title': pick(sc.get('title', '')), 'sub': pick(sc.get('sub', '')), 'l0': pick(sc.get('l0', '')), 'l1': pick(sc.get('l1', '')), 'labels': [{'k': L['k'], 'text': pick(L['text'])} for L in sc.get('labels', [])], **section_profile(sc['from'], sc['to'])})
    for tk in node.get('tally', []):       # emblem keys: t (relative) -> [x, y, z, rotY, scale, split, glow, visible]; positions by lon/lat or model
        v = tk['v'] if 'v' in tk else None
        if v is None:
            x, z = F.model_lonlat(tk['lon'], tk['lat']) if 'lon' in tk else (tk['x'], tk['z'])
            y = tk.get('y', ground_ll(tk['lon'], tk['lat']) if 'lon' in tk else 0) + tk.get('lift', 0)
            v = [x, y, z, tk.get('rot', 0), tk.get('scale', 1), tk.get('split', 0), tk.get('glow', 0), 1 if tk.get('visible', True) else 0]
        tally_keys.append([T(tk['t']), v])
    for ck in node.get('context', []):     # the land beyond the plate (terrain.context): opacity keys, t relative
        ctx_keys.append([T(ck['t']), [float(ck['a'])]])
    for dc in node.get('decals', []):      # graphics drawn on the plate (an emblem, a star map, a rings diagram, a reconstruction plan)
        if dc['kind'] == 'footprints':     # every period city's outline, in its colour, with a label
            dc['eras'] = []
            for nd in FM['nodes']:
                cs = nd.get('city')
                if not cs or nd['id'] in dc.get('skip', []): continue
                rings_ = [w['ring'] for w in cs.get('walls', []) if 'ring' in w] + [f['region'] for f in cs.get('fabric', []) if isinstance(f.get('region'), list)] + cs.get('outline', [])   # outline: a village's ditch
                if not rings_: rings_ = cs.get('hide', [])
                if not rings_: continue
                era_e = next((e for e in eras_out if e['id'] == nd['id']), None)
                mask_ = FOOT.get(nd['id'])
                bnd_ = [[[(x / F.size[0] + .5), (z / F.size[1] + .5)] for x, z in r] for r in era_e['boundary']] if era_e and era_e.get('boundary') else None
                dc['eras'].append({'col': dc.get('palette', {}).get(nd['id'], nd.get('col', '#ffffff')), 'rings': rings_, 'mask': None if bnd_ else mask_, 'uv_rings': bnd_})
                if dc.get('labels', True):
                    lon_ = sum(p_[0] for p_ in rings_[0]) / len(rings_[0]); lat_ = max(p_[1] for r_ in rings_ for p_ in r_)
                    y_ = nd['years'][0]; lz, le = ab(nd.get('label', {}))
                    FM.setdefault('labels', []).append({'lon': lon_, 'lat': lat_, **{l_: P_['year']['label'].format(name=nm_, year=i18n.year(l_, y_)) for l_, P_, nm_ in zip(LANG, PACK, (lz, le))},
                                                        'size': 1.0, 'dmin': 0, 't0': T(dc.get('at', 0)) + 1.0, 't1': node['_t1'] + 1.0})
        k = len(decals_out); assert k < 4, 'at most 4 decals'
        png = DEC.render(dc, F, ST, C, LAYOUT.data(D, f'decal_{k}.png'))
        decals_out.append({'i': k, 'id': dc['id'], 'file': f'data/decal_{k}.png', 'on': T(dc.get('at', 0)), 'fade': dc.get('fade', 1.5), 'off': T(dc.get('off_at')) if 'off_at' in dc else (None if dc.get('persist') else T('end')),
                           'offStyle': dc.get('offStyle', 'fade'), 'offDur': dc.get('offDur', 1.2), 'gain': dc.get('gain', 1.0), 'uv': png['uv'], 'glow': dc.get('glow', 1.0), 'photo_dim': dc.get('photo_dim', 0)})
    if 'satellite' in node:
        s_ = node['satellite']
        epochs_sat = {'on': T(s_.get('at', 0)), 'fade': s_.get('fade', 2.0), 'off': T(s_.get('off_at')) if 'off_at' in s_ else (None if s_.get('persist', True) else T('end')), 'offDur': s_.get('offDur', 1.5), 'gain': s_.get('gain', 1.0), 'sweep': bool(s_.get('sweep', False))}
        if 'back_at' in s_: epochs_sat['back'] = T(s_['back_at']); epochs_sat['backFade'] = s_.get('back_fade', s_.get('fade', 4.0))   # a second line gives the model back
        FM['_satellite'] = epochs_sat
    for ft in node.get('footage', []):
        a_, b_ = ab(ft)
        footage_out.append({'id': ft['id'], 'file': ft['file'], 'on': T(ft.get('at', 0)), 'dur': float(ft['dur']), 'start': float(ft.get('start', 0)), 'fin': ft.get('in', 1.0), 'fout': ft.get('out', 1.0),
                            'title': a_, 'sub': b_, 'kicker': pick(ft['kicker']) if 'kicker' in ft else KICKER_TODAY, 'credit': pick(ft.get('credit', '')), 'pan': ft.get('pan', 0),
                            'mode': ft.get('mode', 'full'), 'side': ft.get('side', 'right'),
                            'anchor': (F.model_lonlat(*ft['anchor']) + [ground_ll(*ft['anchor'])]) if 'anchor' in ft else None,
                            'force': bool(ft.get('force')), '_with': ft.get('with'), '_node': node['id']})   # force: shown over a change on purpose (演出文法 5b)
    for c in node.get('cues', []):
        if 'pause' in c: continue
        a, b = ab(c); cues.append({'id': c['id'], 'node': node['id'], 'later': bool(c.get('later')), 't0': node['_line_t'][c['id']][0], 'a': a, 'b': b, 'extra': c.get('extra', 0.4)})
    for e in node.get('events', []): evs.append({'t': T(e['t']), 'type': e['type'], **{k: v for k, v in e.items() if k not in ('t', 'type')}})
    keys = node.get('camera', [])
    for k in keys:
        tk_ = T(k['t'])
        inside_ = [rid_ for nid_, rid_, (w0_, w1_) in FOLLOW if nid_ == node['id'] and w0_ - .05 < tk_ < w1_ + .05]
        if inside_: print(f'  camera: key at {tk_:.2f} s left out (inside the follow of {inside_[0]}, which ends on the city)'); continue
        cam.append([tk_, camv(k)])
    for qi_, q in enumerate(node['_ins']):   # the camera moves the algorithm inserted (a hold, a closer look), each in its own time
        at_ = node_time(node, q['tau']) + sum(o['delta'] for o in node['_ins'][:qi_] if o['tau'] == q['tau'])   # after earlier ones at the same place
        for off_, kv_ in q['keys']: cam.append([round(at_ + off_, 3), camv(kv_)])
    cursor = node['_t1']

# resolve `until: <node>` epochs / props
for ep in epochs + props_out + eras_out:
    if isinstance(ep['off'], dict): ep['off'] = ep['off']['_t1']
    elif isinstance(ep['off'], tuple): ep['off'] = round(ep['off'][1]['_t0'] + ep['off'][2] * ep['off'][1].get('_k', 1.0), 3)
for ck in OP.get('context', []): ctx_keys.append([float(ck['t']), [float(ck['a'])]])
for tk in OP.get('tally', []):
    v = tk.get('v') or [tk['x'], tk.get('y', 0), tk['z'], tk.get('rot', 0), tk.get('scale', 1), tk.get('split', 0), tk.get('glow', 0), 1 if tk.get('visible', True) else 0]
    tally_keys.append([float(tk['t']), v])
last = cursor
light['lights'] = round(last + float(CL.get('lights_after', 1.5)), 3)
end_t = round(light['lights'] + float(CL.get('end_after', 1.5)), 3)
DUR = round(end_t + float(CL.get('end_hold', 9.0)), 3)
yearline = [[0.0, first_year]] + yearline + [[DUR, yearline[-1][1]]]
def year_time(Y):
    """the first moment the film's year counter reaches Y (after the modern growth starts)"""
    t_on = grow['on'] if grow else 0.0
    for (ta, ya), (tb, yb) in zip(yearline, yearline[1:]):
        if tb < t_on or yb < Y or ya > yb: continue
        if ya >= Y: return round(max(ta, t_on), 3)
        return round(max(t_on, ta + (tb - ta) * (Y - ya) / ((yb - ya) or 1)), 3)
    return yearline[-1][0]
if grow:   # the growth's {year} times and its counters' end, on the whole year line
    # the year line from the growth on, for the engine: today's buildings rise when the counter first reaches their year
    yl_ = [[ta, ya] for ta, ya in yearline if ta >= grow['on'] - 1.0]
    yl_ = [p_ for i_, p_ in enumerate(yl_) if i_ == 0 or p_ != yl_[i_ - 1]]
    assert len(yl_) <= 48, f'the modern year line has {len(yl_)} points; the engine reads 48 (studio.js YLN)'
    grow['yl'] = [[round(ta, 3), round(ya, 3)] for ta, ya in yl_]
    for b in grow['bands']:
        tr_ = b.pop('_traw', None)
        if isinstance(tr_, dict) and 'year' in tr_: b['t'] = round(year_time(float(tr_['year'])) + float(tr_.get('plus', 0)), 3)
    if 'dim' in grow:
        tr_ = grow['dim'].pop('_traw', None)
        if isinstance(tr_, dict) and 'year' in tr_: grow['dim']['t'] = year_time(float(tr_['year']))
    if grow.get('counters'):
        u_ = grow['counters'].pop('_until', None)
        if u_: grow['counters']['t1'] = next(n['_t1'] for n in FM['nodes'] if n['id'] == u_)
# cues: hold >= reading time, never into the next cue or the end card
cues.sort(key=lambda c: c['t0'])
for i, c in enumerate(cues):
    h = max(hold(c['a']), hold(c['b']), (voice_len(c['id']) or 0)); nxt = cues[i + 1]['t0'] if i + 1 < len(cues) else end_t   # (on screen while it is heard)
    c['t1'] = round(min(c['t0'] + h + c['extra'], nxt - 0.08), 3)
    if c['t1'] < c['t0'] + h - 1e-6: print(f'warning: cue {c["id"]} at {c["t0"]:.2f}s needs {h:.1f}s but has {c["t1"] - c["t0"]:.1f}s: give its node more seconds', file=sys.stderr)
    c.pop('extra', None)
# camera: opening keys, then the nodes' keys; a node without keys drifts gently from the previous key
op_keys = [[float(k['t']), camv(k)] for k in OP.get('camera', [])]
cam = op_keys + cam
cam.sort(key=lambda k: k[0])
cl_keys = [[round(light['lights'] + float(k['t']), 3), camv(k)] for k in CL.get('camera', [])]
for tk in CL.get('tally', []):
    v = tk.get('v') or [tk['x'], tk.get('y', 0), tk['z'], tk.get('rot', 0), tk.get('scale', 1), tk.get('split', 0), tk.get('glow', 0), 1 if tk.get('visible', True) else 0]
    tally_keys.append([round(light['lights'] + float(tk['t']), 3), v])
tally_keys.sort(key=lambda k: k[0])
for i in range(1, len(tally_keys)):
    if tally_keys[i][0] <= tally_keys[i - 1][0]: tally_keys[i][0] = round(tally_keys[i - 1][0] + .02, 3)
_tk = []   # visibility is a step, not a fade: a hidden key right before a key that shows the emblem again
for i, k in enumerate(tally_keys):
    if i and k[1][7] > .5 and tally_keys[i - 1][1][7] < .5: _tk.append([round(k[0] - .02, 3), k[1][:7] + [0]])
    _tk.append(k)
tally_keys = _tk
cam += cl_keys
dedup = []
for k in cam:   # a node's first key often sits exactly on the previous node's last key: keep one
    if dedup and k[0] <= dedup[-1][0]:
        if k[1] == dedup[-1][1]: continue
        k = [round(dedup[-1][0] + 0.02, 3), k[1]]
    dedup.append(k)
cam = dedup
for i in range(1, len(cam)):   # a camera never spins the long way round: every key's azimuth within 180 degrees of the one before
    cam[i][1][3] = round(stagecraft.unwrap(cam[i][1][3], cam[i - 1][1][3]), 3)
if FOLLOW:   # a camera that follows a beam owns its window: any other key inside it goes (with a note)
    fk_ = set()
    for _, rid_, (w0_, w1_) in FOLLOW:
        for k in cam:
            if w0_ - .01 <= k[0] <= w1_ + .01: fk_.add(id(k))
    drop = [k for k in cam if id(k) in fk_ and not any(abs(k[0] - k2[0]) < 1e-6 and k[1] == k2[1] for k2 in FOLLOW_KEYS)]
    for k in drop: print(f'  camera: key at {k[0]:.2f} s dropped (inside a beam follow)')
    cam = [k for k in cam if not any(k is d_ for d_ in drop)]
for i in range(len(cam) - 1):
    assert cam[i][0] < cam[i + 1][0], f'camera keys must increase in time: {cam[i][0]} -> {cam[i + 1][0]}'
if cam[-1][0] < DUR: cam.append([DUR, cam[-1][1]])

# ------------------------------------------------------------------ stagecraft: rings and the cities' timing, from the final camera
CAMERA = stagecraft.Camera(cam, FM.get('fov', 30))
# a full-screen clip covers the picture: the camera holds nothing under it, so a city's change waits until the clip is gone (SKILL.md
# 演出文法 5b; the 3D clock itself runs on: engine/main.js only stops drawing the scene under a clip in the live preview). Also the
# one place the camera may cut (演出文法 F)
def covered(t): return any(f['mode'] == 'full' and f['on'] + f['fin'] <= t <= f['on'] + f['dur'] - f['fout'] for f in footage_out)
if os.environ.get('CAMDBG'):
    for k in cam:
        if 140 < k[0] < 200: print('   cam', k[0], [round(v, 4) if isinstance(v, float) else v for v in k[1]])
    print('   FOLLOW', FOLLOW)
PW_, PD_ = F.size
def far_corner(o): return max(math.hypot(sx * PW_ / 2 - o[0], sz * PD_ / 2 - o[1]) for sx in (-1, 1) for sz in (-1, 1)) + .1
def view_r(t, o):   # how far from o a ring stays on screen at t (falls back to the frame at the camera's target)
    r = CAMERA.view_radius(t, (o[0], model_ground(*o), o[1]))
    if r <= 0: p_, g_, fov_, _ = CAMERA.at(t); r = math.dist(p_, g_) * math.tan(math.radians(fov_) / 2) * stagecraft.ASPECT
    return r
def ring_fit(t, o):   # the largest ring round o the camera shows whole at t, aimed at o (as the contracting ring's camera turns to be)
    v_ = CAMERA.state(t); v_[:3] = [o[0], model_ground(*o), o[1]]
    return stagecraft.fit_radius(v_, o, model_ground(*o), TIMING['ring_fit_x'], TIMING['ring_fit_y'])
TIMED = []
for e in eras_out:   # each city: when every building rises (stages, settle) and the light of its change
    pd = e.pop('_pend'); cs, node, prims = pd['cs'], pd['node'], pd['prims']
    on_, span_, ranks_, fronts_, grow_ = era_times(prims, pd['meta'], cs, pd['at_of'], CAMERA, node['_t0'], node['_t1'], IMPACT.get(node['id']), node['id'])
    TIMED.append((e, pd, ranks_))
    e.update({'on': round(on_, 3), 'span': round(span_, 3), 'grow': grow_, 'rise': round(span_ + grow_, 3), 'fronts': fronts_})
    print(f'  city {node["id"]}: {len(prims)} primitives, rises {on_:.1f}-{on_ + span_ + grow_:.1f} s, ' + ', '.join(f'{f_["mode"]} {f_["curve"][0][0]:.1f}-{f_["curve"][1][0]:.1f}' for f_ in fronts_))

def plan_stages():
    """SKILL.md 演出文法 9e: what the camera must still give each stage, as time inserted into its node.
    (a) a stage starts on the first camera key that frames its place: the camera stops there (a hold) rather than the stage
        waiting for a later shot; (b) the camera holds the place until hold_after seconds after its last building is up;
    (c) a place seen only small is looked at closer (look_size of the frame's height, look_secs seconds), then the camera
        goes back to where it was. One finding per stage and pass; compile runs again until there is none."""
    new = []
    state = lambda t: [round(v, 6) for v in CAMERA.state(t)]
    key_ = lambda v: {'v': v[:6], 'fov': v[6]}
    in_follow = lambda t: any(w0 - .05 <= t <= w1 + .05 for _, _, (w0, w1) in FOLLOW)
    for e in eras_out:
        node = next(n for n in FM['nodes'] if n['id'] == e['id'])
        # a staged sequence owns its time (the sky plan, like a beam follow): nothing is inserted inside it
        owned = lambda t, _n=node: any(w0 - .05 <= t <= w1 + .05 for w0, w1 in _n.get('_owned', []))
        for f in e['fronts']:
            P = f['_plan']; C_, R_ = P['centre'], P['rad']; need_end = P['t_end'] + TIMING['hold_after']
            # (a) an earlier key aims at the place (near the middle of the frame, a fifth of its height or more), but the camera
            # does not stop there
            framed = lambda t: (lambda q: q is not None and abs(q[0]) <= .35 and abs(q[1]) <= .45)(CAMERA.project(t, C_)) and stagecraft.size_on_screen(CAMERA, t, C_, R_) >= .2
            early = [k[0] for k in cam if P['t_from'] - 1e-6 <= k[0] < P['t0'] - 1.2 and node['_t0'] <= k[0] < node['_t1'] and not in_follow(k[0]) and not owned(k[0]) and not covered(k[0]) and framed(k[0])]
            if early:
                tk = early[0]; dl = round(need_end - P['t0'] + .5, 2)
                new.append((node, {'tau': round(node_rel(node, tk) + 1e-3, 4), 'delta': dl, 'keys': [[dl, key_(state(tk))]], 'kind': 'start', 'why': f'stage of {e["id"]} starts on the key at {tk:.1f} s (was {P["t0"]:.1f} s)'})); continue
            # (b) the camera leaves before the stage is done and seen
            t, bad, leave = P['t0'], 0, None
            while t <= need_end:
                bad = bad + 1 if not stagecraft.holding(CAMERA, C_, R_, t, hidden=covered) else 0
                if bad >= 3: leave = round(t - .3, 2); break
                t += .1
            if leave is not None and not in_follow(leave) and not owned(leave):
                dl = round(need_end - leave + .3, 2); S_ = state(leave - .1)
                new.append((node, {'tau': round(node_rel(node, leave - .1), 4), 'delta': dl, 'keys': [[.001, key_(S_)], [dl, key_(S_)]], 'kind': 'hold', 'why': f'hold on {e["id"]} until {need_end:.1f} s (the camera left at {leave:.1f} s)'})); continue
            # (c) never seen close: once the city (all its stages under way by then) stands, a closer look at its key building
            # (look_target: named, drawn in light, any landmark; never the houses). Seen close = that building on screen (inside
            # 80 % of the frame) near enough that a look_focus_m patch round it fills look_size of the frame's height, for
            # look_secs, at any time in the node (its own close shots count). Not for a sweep along a line.
            if P['n'] < TIMING['look_min_n'] or f['mode'] == 'line' or P['focus'] is None: continue
            Rf = TIMING['look_focus_m'] * F.scale; run, best, t = 0, 0, P['t0']; Fc = P['focus']['c']
            while t <= node['_t1']:
                q_ = CAMERA.project(t, Fc); fov_ = CAMERA.at(t)[2]
                ok = q_ is not None and abs(q_[0]) <= .8 and abs(q_[1]) <= .8 and Rf / (q_[2] * math.tan(math.radians(fov_) / 2)) >= TIMING['look_size']
                run = run + 1 if ok else 0; best = max(best, run); t += .1
            if best * .1 >= TIMING['look_secs']: continue
            t_l = max([q['_plan']['t_end'] for q in e['fronts'] if q['_plan']['t0'] <= P['t_end']] + [P['t_end']]) + TIMING['hold_after']
            t_l = min(t_l, node['_t1'] - .2)
            if owned(t_l): continue
            S_ = state(t_l)
            L1 = stagecraft.look_view(Fc, Rf, S_[3] + 12, 34, S_[6], .55); L2 = stagecraft.look_view(Fc, Rf * .92, S_[3] + 30, 30, S_[6], .55)
            A1 = stagecraft.move_time(S_, L1, speed=.5); dl = round(A1 + TIMING['look_secs'] + .3, 2)   # then on to the next key (paced)
            new.append((node, {'tau': round(node_rel(node, t_l), 4), 'delta': dl, 'keys': [[.001, key_(S_)], [round(A1, 2), key_(L1)], [round(A1 + TIMING['look_secs'], 2), key_(L2)]],
                               'kind': 'look', 'why': f'a closer look at {e["id"]} ({P["focus"]["what"]}, rank {P["focus"]["rank"]}) after {t_l:.1f} s (seen close at most {best * .1:.1f} s)'}))
    return new

NEWPLAN = plan_stages()
if NEWPLAN:
    for node, q in NEWPLAN:
        print(f'  plan (pass {PASS}): node {node["id"]} +{q["delta"]:.1f} s at {q["tau"]:.2f}: {q["why"]}')
        if any(abs(o['tau'] - q['tau']) < .05 and o.get('kind') == q['kind'] for o in PLAN.get(node['id'], [])):
            raise SystemExit(f'compile: the stage plan repeats itself in node {node["id"]} ({q["why"]}): the inserted keys do not give what the stage needs')
        if q['kind'] == 'start':   # the stage moves to an earlier key: what was planned after it was planned for the old start
            PLAN[node['id']] = [o for o in PLAN.get(node['id'], []) if not (o.get('kind') in ('hold', 'look') and o['tau'] > q['tau'])]
        PLAN.setdefault(node['id'], []).append(q)
    if PASS >= int(os.environ.get('CT_MAX_PASS') or 6): raise SystemExit(f'compile: the stage plan did not settle in {PASS} passes')
    json.dump(PLAN, open(LAYOUT.logs(D, 'plan.json'), 'w'), ensure_ascii=False, indent=1)   # what the algorithm inserted (for reading)
    sys.stdout.flush(); os.environ['CT_PLAN'] = json.dumps(PLAN); os.environ['CT_PASS'] = str(PASS + 1)
    os.execv(sys.executable, [sys.executable, '-I', os.path.abspath(__file__), D])
if PLAN: print(f'  plan: {sum(len(v) for v in PLAN.values())} insertions after {PASS} passes, ' + ', '.join(f'{k} +{sum(q["delta"] for q in v):.1f} s' for k, v in PLAN.items()))
# one front at a time: the engine draws a single front per city (engine/main.js: the stage growing now), so a second stage running
# at the same time rises with no light ahead of it (帝都 2026-10-21: the new quarters came up before the sweep reached them)
for e in eras_out:
    fr_ = sorted(e['fronts'], key=lambda q: q['a'][0])
    for p_, q_ in zip(fr_, fr_[1:]):
        if q_['a'][0] < p_['a'][1] - .5:
            raise SystemExit(f"compile: era {e['id']}: two stages grow at once ({p_['mode']} {p_['a'][0]:.1f}-{p_['a'][1]:.1f} s, {q_['mode']} "
                             f"{q_['a'][0]:.1f}-{q_['a'][1]:.1f} s); the engine lights one front per city: run them one after another or make them one stage")
PLACES = []   # where each city changes and when (era, [t0, t1], centre, radius): may a half-screen picture show then (演出文法 5b)
for e, pd, ranks_ in TIMED:   # write the cities (ranks), their hide masks and edge fields
    cs, node, prims = pd['cs'], pd['node'], pd['prims']
    for f in e['fronts']:
        P_ = f.pop('_plan', None)
        if P_: PLACES.append((e['id'], f['a'], P_['centre'], P_['rad'], [f['a'][0], P_['t_end']]))   # (a: the front's light, to its run-off; then while buildings rise)
    for p, r in zip(prims, ranks_): p[10] = round(r, 5)
    json.dump({'prims': prims}, open(LAYOUT.build(D, e['file']), 'w'), separators=(',', ':'))   # (film.json's file references are relative to build/)
    fx_, fz_ = F.model_lonlat(*(cs.get('fall_from') or cs['origin']))
    e['fallC'] = [round(fx_, 5), round(fz_, 5)]
    e['_dist'] = [math.hypot(p[15] - fx_, p[16] - fz_) for p in prims]; e['_bc'] = [(p[15], p[16]) for p in prims]
    if e.get('hide') is not None:
        cs_ = Seen(dict.items(cs)); cs_.read, cs_.mine = cs.read, set(); cs_['_id'] = node['id']   # (what hide_layer reads, read on cs)
        hide_regions[e['hide']] = hide_layer(prims, cs_, pd['bnd'])
        ED = float(FM.get('era_look', {}).get('edge_m', 150)) * F.scale; img_, rect_ = edge_sdf(pd['bnd'], ED); EDGES[e['hide']] = img_; e['edgeRect'] = rect_; e['edgeD'] = round(ED, 6)
for i_, (nd, node) in enumerate(zip(nodes_out, FM['nodes'])):   # each node's colour ring, sent when its change starts (SKILL.md 演出文法 1)
    imp = IMPACT.get(node['id']); era_ = next((e for e in eras_out if e['id'] == node['id']), None)
    grows_ = bool(era_ and era_.get('fronts')); f0_ = min(era_['fronts'], key=lambda f_: f_['curve'][0][0]) if grows_ else None
    if imp and not (imp['follow'] and grows_): o, t0 = imp['end'], imp['land']   # from its beam's landing
    elif grows_:   # with its city: from where the city starts, when it starts (a followed beam: once the camera has turned to the city)
        o, t0 = f0_['o'], round(max(nd['t0'], f0_['curve'][0][0] - .15), 3)
    else: o, t0 = nd['wave'], nd['t0']                            # else from where the story was, at the node's start
    nd['wave'] = [round(o[0], 5), round(o[1], 5)]
    pv_ = nodes_out[i_ - 1] if i_ else None   # nothing changes inside it (same colour, no city, no reset): drawn without a front
    silent = bool(pv_ and nd['col'] == pv_['col'] and nd['tint'] == pv_['tint'] and not era_ and nd['reset'] is None and 'dim_today' not in node)
    if grows_ and (not imp or imp['follow']) and f0_['mode'] == 'ring': silent = True   # the city's own ring draws the front (two fronts on one spot made a glowing disc)
    nd['ring'] = {'o': nd['wave'], 't0': t0, 'impact': bool(imp), 'shock': [imp['land'], round(imp['end'][0], 5), round(imp['end'][1], 5), round(.9 * view_r(imp['land'], imp['end']), 5)] if imp else None,   # (sized on the landing shot) 'silent': silent,
                  'curve': stagecraft.ring_curve(t0, view_r(t0, o), far_corner(o), TIMING['ring_view'], TIMING['ring_out'])}
for e in eras_out:   # how each city is taken back: contracting from its edge (in) or by the next node's colour ring (out)
    if e.get('off') is None: e['fallR'] = None; continue
    if e['fall'] == 'in':   # cities that burn together share one ring
        same = [q for q in eras_out if q['fall'] == 'in' and q.get('off') == e['off'] and q['fallC'] == e['fallC']]
        maxd = max(max(q['_dist']) for q in same) + 30 * F.scale
        curve = stagecraft.contract_curve(e['off'], maxd, ring_fit(e['off'], e['fallC']), float(e['sink']), t_out=TIMING['contract_in'])
        e['fallR'] = {'mode': 'in', 'o': e['fallC'], 'curve': curve, 'hit': e['off'], 'gone': round(curve[-1][0] + e['fallDur'], 3)}
    else:
        nd = next((q for q in nodes_out if abs(q['t0'] - e['off']) < .06), None)
        if nd is None: o = e['fallC']; curve = stagecraft.ring_curve(e['off'], view_r(e['off'], o), far_corner(o))
        else: o, curve = nd['ring']['o'], nd['ring']['curve']
        dd = [math.hypot(x - o[0], z - o[1]) for x, z in e['_bc']]; near_, reach_ = min(dd), max(dd) + .02
        t_hit = next((t for t, R in curve if R >= near_), curve[-1][0]); t_all = next((t for t, R in curve if R >= reach_), curve[-1][0])
        e['fallR'] = {'mode': 'out', 'o': o, 'curve': curve, 'hit': t_hit, 'gone': round(t_all + e['fallDur'], 3)}
for e in eras_out: e.pop('_dist', None); e.pop('_bc', None)
# a city taken back by a contracting ring: the camera comes down with the ring (SKILL.md 演出文法 9g), from where it is when the
# ring reaches the city to the next key after the ring has closed (the ruins). The ring stays whole on screen all the way: the
# camera comes no nearer than the distance that frames the ring as it is at that moment, so it always moves slower than the
# ring (the distance shrinks as the root of the ring, the ring shrinks on screen too); target, azimuth and elevation ease over.
done_ = set()
for e in eras_out:
    FR = e.get('fallR')
    if not FR or FR['mode'] != 'in' or (FR['hit'], tuple(FR['o'])) in done_: continue
    done_.add((FR['hit'], tuple(FR['o']))); curve = FR['curve']; ts, te = FR['hit'], curve[-1][0]
    nxt = [k for k in cam if te < k[0] <= te + 8]
    S0 = CAMERA.state(ts); ox_, oz_ = FR['o']; oy_ = model_ground(ox_, oz_)
    E_ = list(nxt[0][1]) if nxt else [ox_, oy_, oz_, S0[3] + 12, 30.0, TIMING['ruins_d'], S0[6]]
    E_[3] = stagecraft.unwrap(E_[3], S0[3])
    R0 = max(1e-6, ring_fit(ts, FR['o'])); keys_ = []; t = ts; O_ = [ox_, oy_, oz_]
    t_in = next((tc for tc, rc in curve if rc <= R0 * 1.001), ts)   # the ring is inside the frame from here
    T_ = te - ts + 1.5   # azimuth and elevation ease over until 1.5 s after the ring has closed; the target turns to the ring's
    sm_ = lambda x: (lambda c: c * c * (3 - 2 * c))(min(1.0, max(0.0, x)))   # centre while it sweeps in, then on to the ruins key
    while t < te + 1.5 + 1e-6:
        R_ = stagecraft.curve_at(curve, t); p_ = sm_((t - ts) / T_)
        tg_ = [S0[j] + (O_[j] - S0[j]) * sm_((t - ts) / max(.3, t_in - ts)) for j in (0, 1, 2)] if t <= t_in else [O_[j] + (E_[j] - O_[j]) * sm_((t - t_in) / max(.3, te + 1.5 - t_in)) for j in (0, 1, 2)]
        v_ = tg_ + [S0[3] + (E_[3] - S0[3]) * p_, S0[4] + (E_[4] - S0[4]) * p_, 0.0, S0[6]]
        v_[5] = min(S0[5], max(E_[5], S0[5] * math.sqrt(max(0.0, R_) / R0)))
        if 0 < R_ <= R0 * 1.001:   # (still sweeping in from beyond the frame: not yet)
            v_ = stagecraft.fit_distance(v_, stagecraft.circle(FR['o'], R_, oy_), TIMING['ring_fit_x'], TIMING['ring_fit_y'], d_lo=v_[5])
        keys_.append([round(t, 3), [round(x, 6) for x in v_]]); t += .25
    cam = [k for k in cam if not (ts - .01 <= k[0] <= te + 1.51)] + keys_
    cam.sort(key=lambda k: k[0]); print(f'  camera: comes down with the closing ring {ts:.1f}-{te:.1f} s ({len(keys_)} keys, {S0[5]:.2f} -> {keys_[-1][1][5]:.2f})')
CAMERA = stagecraft.Camera(cam, FM.get('fov', 30))
# no cuts: the camera never jumps (SKILL.md 演出文法 F), except behind a full-screen clip (covered)
jumps = []; t = 0.0
while t < DUR - .5:
    a0, a1 = CAMERA.state(t), CAMERA.state(t + .5)
    wide = 2 * math.sqrt(max(a0[5], 1e-4) * max(a1[5], 1e-4)) * math.tan(math.radians(a0[6]) / 2) * stagecraft.ASPECT
    mv = math.dist(a0[:3], a1[:3]) / wide; turn = abs(a1[3] - a0[3]); zoom = abs(math.log(max(a1[5], 1e-4) / max(a0[5], 1e-4))) / math.log(2)
    if (mv > 1.0 or turn > 60 or zoom > 1.5) and not covered(t) and not covered(t + .5): jumps.append((round(t, 1), round(mv, 2), round(turn), round(zoom, 2)))
    t += .25
if jumps:
    seen_ = set()
    for j_ in jumps[:12]:
        print(f'    jump at {j_[0]} s: target {j_[1]} frames, turn {j_[2]} deg, zoom {j_[3]} doublings in 0.5 s')
        for k in cam:
            if j_[0] - 3 <= k[0] <= j_[0] + 3 and k[0] not in seen_: seen_.add(k[0]); print(f'        key {k[0]:8.2f}  ' + ' '.join(f'{v:.4f}' if isinstance(v, float) else str(v) for v in k[1]))
    raise SystemExit(f'compile: the camera jumps {len(jumps)} times (more than a frame, 60 degrees or 1.5 zoom doublings in half a second): give the move time')
# a pin shows only what is on screen (SKILL.md 演出文法 9h): its place in the picture for most of its time. A tour stop frames its
# pins (tour_subjects), so there an error; elsewhere still a warning (the film-wide pass)
off_ = []
ctx_keys.sort(key=lambda k: k[0])
def _ctx_a(t):   # the land beyond the plate's opacity at t (linear between keys, held beyond them)
    if not ctx_keys: return 0.0
    if t <= ctx_keys[0][0]: return ctx_keys[0][1][0]
    for (ta, (a,)), (tb, (b,)) in zip(ctx_keys, ctx_keys[1:]):
        if t <= tb: return a + (b - a) * (t - ta) / max(1e-9, tb - ta)
    return ctx_keys[-1][1][0]
CTX_OUT = None   # the land beyond the plate for the engine: its relief file, where it lies, how its heights read, when it shows
if _cj and ctx_keys:
    CTX_OUT = {'file': 'data/context16.png', 'rect': _cj['rect_model'], 'lo': _cj['min_m'], 'hi': _cj['max_m'], 'ref': _tj['min_m'], 'ex': _tex, 'exFar': _CTXX, 'blend': _CTXB,
               'fade': float(C['terrain']['context'].get('fade_km', 10)) * 1000 * F.scale, 'col': C['terrain']['context'].get('col'),
               'shade': C['terrain']['context'].get('shade'), 'keys': ctx_keys}
elif ctx_keys: print('warning: context keys but no build/data/context.json (run pipeline/terrain.py with terrain.context)', file=sys.stderr)
for p in pins:   # a pin points at something on the plate, or on the land beyond it while that is shown: anything else floats over the void
    if abs(p['pos'][0]) > F.size[0] / 2 or abs(p['pos'][1]) > F.size[1] / 2:
        on_ctx = CTX_RECT and CTX_RECT[0] <= p['pos'][0] <= CTX_RECT[1] and CTX_RECT[2] <= p['pos'][1] <= CTX_RECT[3]
        if not on_ctx:
            raise SystemExit(f'compile: pin {p["id"]} ({p["_node"]}) is anchored off the plate: point it at the part of the place that lies on the plate (or give the city a terrain.context that covers it)')
        dark = [p['t0'] + i * .25 for i in range(int((p['t1'] - p['t0']) / .25) + 1) if _ctx_a(p['t0'] + i * .25) < .5]
        if dark: raise SystemExit(f'compile: pin {p["id"]} ({p["_node"]}) stands on the land beyond the plate, which is not shown at {dark[0]:.1f} s: show it (context keys) for the pin\'s whole time')
for p in pins:
    if p['_offok']: continue
    X = (p['pos'][0], p['pos'][2] + .002, p['pos'][1]); n_ = ok_ = 0; t = p['t0'] + .4
    while t <= p['t1'] - .4:
        q = CAMERA.project(t, X); n_ += 1; ok_ += 1 if (q is not None and abs(q[0]) <= .92 and abs(q[1]) <= .92) else 0; t += .25
    if n_ and ok_ / n_ < .7: off_.append(p)
for p in off_: print(f'  {"error" if p["_tour"] else "warning"}: pin {p["id"]} ({p["_node"]}, {p["t0"]:.1f}-{p["t1"]:.1f} s) is off screen most of its time')
if any(p['_tour'] for p in off_) and not os.environ.get('CT_PINWARN'): raise SystemExit('compile: a tour stop shows a pin whose place is not on screen: frame it (tour_subjects) or mark it offscreen_ok')
for p in pins:
    for k_ in ('_node', '_tour', '_offok'): p.pop(k_, None)
# today's buildings rise when they can be seen (SKILL.md 演出文法 7): at the moment the counter reaches a building's year, or, if
# the camera is not looking there then, the first moment after it that the building is in the frame (and no full-screen clip
# covers the picture). Buildings that come into view together rise over a few seconds in the order of their years, not in one
# burst. data/grow_t.json lists only the buildings that wait; the rest rise with the counter (the engine's tOfYear)
if grow and grow.get('yl'):
    import numpy as np
    yl_ = grow['yl']
    def t_of_year(y):
        for (t0_, y0_), (t1_, y1_) in zip(yl_, yl_[1:]):
            if y1_ >= y: return t0_ if y0_ >= y else t0_ + (t1_ - t0_) * (y - y0_) / max(y1_ - y0_, 1e-4)
        return 1e6
    early_ = {i_: y_ for i_, y_ in (CHANGE or {}).get('early', [])}
    reset_y = next((float(n['reset']['year']) for n in FM['nodes'] if n.get('reset')), -1e9)
    ids_, pts_, yrs_ = [], [], []
    for i_, (bi_, h_, rings_, base_) in enumerate(_MODEL['p']):
        y_ = early_.get(i_, _MODEL['b'][bi_][0])
        if not y_ or y_ <= reset_y: continue   # (standing before the growth starts, or undated)
        r_ = rings_[0]; ids_.append(i_); yrs_.append(y_)
        pts_.append((sum(q[0] for q in r_) / len(r_), (base_ or 0) + h_ * .5, sum(q[1] for q in r_) / len(r_)))
    P_ = np.array(pts_); ty_ = np.array([t_of_year(y_ - .5) for y_ in yrs_]); seen_ = np.full(len(ids_), np.nan)
    t_end = next(n['_t0'] for n in FM['nodes'] if n['id'] == 'today') if any(n['id'] == 'today' for n in FM['nodes']) else DUR
    t = float(ty_.min()) if len(ty_) else t_end
    while t <= t_end + 1e-6 and np.isnan(seen_).any():
        if not covered(t):
            p_, g_, fov_, _ = CAMERA.at(t)
            f_ = np.subtract(g_, p_); f_ /= np.linalg.norm(f_); r_ = np.array([-f_[2], 0., f_[0]]); r_ /= np.linalg.norm(r_); u_ = np.cross(r_, f_)
            V_ = P_ - p_; z_ = V_ @ f_; th_ = math.tan(math.radians(fov_) / 2)
            with np.errstate(divide='ignore', invalid='ignore'):
                x_ = (V_ @ r_) / (z_ * th_ * stagecraft.ASPECT); y_ = (V_ @ u_) / (z_ * th_)
            vis_ = (z_ > 1e-4) & (np.abs(x_) < .92) & (np.abs(y_) < .85) & np.isnan(seen_) & (ty_ <= t + .125)
            seen_[vis_] = t
        t += .25
    late_ = ~np.isnan(seen_) & (seen_ > ty_ + .5)
    out_ = []
    for t_ in np.unique(seen_[late_]):   # those entering the frame together: oldest first, longer for more (a whole district, up to see_max)
        k_ = np.where(late_ & (seen_ == t_))[0]; k_ = k_[np.argsort(np.array(yrs_)[k_], kind='stable')]
        sp_ = min(TIMING['see_max'], max(TIMING['see_min'], TIMING['see_rate'] * len(k_)))
        out_ += [[ids_[j_], round(float(t_) + sp_ * n_ / max(1, len(k_)), 3)] for n_, j_ in enumerate(k_)]
    json.dump(out_, open(LAYOUT.data(D, 'grow_t.json'), 'w'), separators=(',', ':'))
    GROW_T = sorted(t_ for _, t_ in out_)   # (for the dead-air check: today's buildings rising as the camera finds them)
    grow['tfile'] = 'data/grow_t.json'
    print(f'  growth: {len(ids_)} buildings rise with the counter; {len(out_)} wait until the camera sees them, '
          f'{int(np.isnan(seen_).sum())} are never in view before the end (they rise with the counter, unseen)')
# masks -> two RGBA textures
hch = list(hide_regions[:8])
while len(hch) < 8: hch.append(Image.new('L', (HW, HH), 0))
Image.merge('RGBA', hch[:4]).save(LAYOUT.data(D, 'hide.png'))
try:   # locator base: today's footprints (grey) and the river (blue) on a dark ground
    import numpy as _np
    LW = 600; LH = round(LW * F.size[1] / F.size[0])
    base_ = Image.new('RGB', (LW, LH), (18, 20, 26)); dlo = ImageDraw.Draw(base_)
    Mj = json.load(open(LAYOUT.data(D, 'model.json')))
    for p in Mj['p']:
        ring = p[2][0]; dlo.polygon([((x / F.size[0] + .5) * LW, (z / F.size[1] + .5) * LH) for x, z in ring], fill=(88, 92, 104))
    wimg = Image.open(LAYOUT.data(D, 'water.png')).convert('L').resize((LW, LH))
    base_.paste(Image.new('RGB', (LW, LH), (74, 120, 190)), (0, 0), wimg)
    base_.save(LAYOUT.data(D, 'locator.png'))
except Exception as ex:
    print('locator: skipped', ex)
Image.merge('RGBA', hch[4:8]).save(LAYOUT.data(D, 'hide2.png'))
ech = list(EDGES[:8])
while len(ech) < 8: ech.append(Image.new('L', (EW, EW), 255))
Image.merge('RGBA', ech[:4]).save(LAYOUT.data(D, 'edge.png')); Image.merge('RGBA', ech[4:8]).save(LAYOUT.data(D, 'edge2.png'))
while len(mask_chans) < 12: mask_chans.append(Image.new('L', (MW, MH), 0))
Image.merge('RGBA', mask_chans[0:4]).save(LAYOUT.data(D, 'layers1.png'))
Image.merge('RGBA', mask_chans[4:8]).save(LAYOUT.data(D, 'layers2.png'))
Image.merge('RGBA', mask_chans[8:12]).save(LAYOUT.data(D, 'layers3.png'))   # (studio.js EMAX)
# timeline bar: film time on the x axis, a tick at each node's first year
bar = {'ticks': [{'t': nd['t0'], 'year': nd['years'][0], 'label': nd['label']} for nd in nodes_out], 'from': light['lamp'], 'to': last}
E = FM.get('end', CL.get('end', {}))
# the credits (the user, 2026-10-22): end.credits {author, voice, music, ...}, each a text or per language (the author's with a
# contact or a site), one line each above the sources and as bright as the first of them; a role's name is the language pack's
# word credit_<role>; an empty one is left out
_credits = [f"{i18n.word(LANG[0], 'credit_' + k_)}　{pick(v_)}" for k_, v_ in (E.get('credits') or {}).items() if v_]
end = {'t': end_t, 'title_a': tx(E.get(LANG[0] + '_title') or E.get('title_a')), 'title_b': tx(E.get(LANG[1] + '_title') if len(LANG) > 1 else None) or tx(E.get('title_b')), 'rule': E.get('rule', FM['palette'].get('pick', '#ffa13d')),
       'lines': _credits + [pick(s) for s in E.get('lines', [])], 'bright': max(1, len(_credits))}
op_cue = OP.get('cue')
if op_cue:
    a, b = ab(op_cue); t0 = float(op_cue.get('t', 1.0)); cues.insert(0, {'id': op_cue.get('id', 'opening'), 'node': None, 'later': False, 't0': t0, 't1': round(min(t0 + max(hold(a), hold(b)) + .4, cues[0]['t0'] - .08 if cues else light['lamp']), 3), 'a': a, 'b': b})
sat = FM.get('_satellite')
def sat_out(sat):
    """the satellite plate: the higher-resolution mosaic (pipeline/imagery_tiles.py, internal tests only) when the film asks for it,
    else Sentinel-2 (pipeline/satellite.py)"""
    if not sat: return None
    hr = FM.get('satellite_source') == 'hr' and os.path.exists(LAYOUT.data(D, 'satellite_hr.jpg'))
    f, meta = ('data/satellite_hr.jpg', 'data/satellite_hr.json') if hr else ('data/satellite.png', 'data/satellite.json')
    if not os.path.exists(LAYOUT.build(D, f)): return None
    return {**sat, 'file': f, 'credit': json.load(open(LAYOUT.build(D, meta))).get('credit', '')}
# tags (pins and place names): pole length and side chosen once per stretch they show (pipeline/tags.py, SKILL.md 演出文法 G)
import tags as TAGS
labels_out = [{'pos': F.model_lonlat(L['lon'], L['lat']) + [ground_ll(L['lon'], L['lat'])], 'a': ab(L)[0], 'b': ab(L)[1], 'size': L.get('size', 1), 'dmin': L.get('dmin', .8),
               't0': float(L.get('t0', 0)), 't1': float(L.get('t1', 1e9))} for L in FM.get('labels', [])]
for L in labels_out:   # a place a tour stop is about keeps its name from the flight there to the end of the stop, however near the
    # camera comes (place names otherwise show on wide shots only): the name never goes as the camera arrives
    L['keep'] = [[n['_t0'], n['_t1']] for n in FM['nodes'] if n.get('_subj') and min(math.hypot(L['pos'][0] - q[0], L['pos'][1] - q[2]) for q in n['_subj']) <= .15]
def _spans(vis, a, b, step=.25):
    out, s0, t = [], None, a
    while t <= b:
        if vis(t) and s0 is None: s0 = t
        if not vis(t) and s0 is not None: out.append((s0, t - step)); s0 = None
        t += step
    if s0 is not None: out.append((s0, b))
    return [sp for sp in out if sp[1] - sp[0] >= .5]
tag_list = []
for p in pins:
    tag_list.append({'id': 'pin:' + p['id'], 'pos': (p['pos'][0], (p['pos'][2] if len(p['pos']) > 2 else 0) + .002, p['pos'][1]), 'spans': [(p['t0'], p['t1'])], 'visible': lambda t: True, 'text': p['text'], 'sub': p['sub']})
for li, L in enumerate(labels_out):
    a0, a1 = max(light['lamp'] + 1, L['t0']), min(light['lights'], L['t1'])
    vis = (lambda L_: lambda t: (CAMERA.at(t)[3] >= L_['dmin'] - .05 or any(k0 <= t <= k1 for k0, k1 in L_['keep'])) and not covered(t))(L)
    tag_list.append({'id': f'label:{li}', 'pos': (L['pos'][0], L['pos'][2] + .004, L['pos'][1]), 'spans': _spans(vis, a0, a1), 'visible': vis, 'text': L['a'], 'sub': L['b']})
LAY = TAGS.layout(tag_list, CAMERA.project)
for p in pins:
    if 'pin:' + p['id'] in LAY: _, _, p['len'], p['left'] = LAY['pin:' + p['id']][0]
for li, L in enumerate(labels_out): L['lay'] = LAY.get(f'label:{li}', [])
print(f'  tags: {len(pins)} pins, {len(labels_out)} place names laid out in {sum(len(v) for v in LAY.values())} stretches')
_core = lambda s: re.split(r'\s*[·（(]\s*', s or '')[0].strip()
for p in pins:   # one place, two tags at once: a pin named like a place name (film.labels) shown at the same time (SKILL.md 演出文法 9h)
    for L in labels_out:
        both_ = [(max(p['t0'], s0), min(p['t1'], s1)) for s0, s1, _, _ in L['lay'] if s0 < p['t1'] and p['t0'] < s1]
        if _core(p['text']) and _core(p['text']) == _core(L['a']) and both_:
            WARN.append(f'pin {p["id"]} and the place name "{L["a"]}" show together {both_[0][0]:.1f}-{both_[0][1]:.1f} s: one place, two tags; '
                        f'drop the pin or give it what the name does not say')
film = {
    'dur': DUR, 'fov': FM.get('fov', 30), 'yearFmt': FM.get('yearFmt', 'zh'), 'identity': {'l1': pick(FM['identity']['l1']), 'l2': pick(FM['identity']['l2'])},
    'palette': FM['palette'], 'light': {**light, 'base': FM.get('light', {}).get('base', 0.28)},
    'bands': [{'lo': b['lo'], 'hi': b['hi'], 'label': tx(b.get(LANG[0]) or b.get('zh') or b.get('en')), 'n': ST['bands'][k]['n']} for k, b in enumerate(bands)],
    'yearline': yearline, 'nodes': nodes_out, 'bar': bar,
    'epochs': epochs, 'lines': lines, 'grow': grow, 'height': height, 'pick': picks, 'camera': cam, 'pins': pins, 'marks': marks, 'ranges': ranges, 'readouts': readouts, 'cues': cues,
    'decals': decals_out, 'satellite': sat_out(sat),
    'footage': footage_out, 'end': end, 'ev': evs, 'music': FM.get('music', {}),
    'labels': labels_out,
    'props': props_out, 'tally': {'keys': tally_keys}, 'rise': FM.get('rise', {}), 'drift': FM.get('drift', 1.0), 'sections': sections, 'eras': eras_out, 'night': night_keys, 'routes': routes_out,
    'era_look': {k_: FM.get('era_look', {}).get(k_, d_) for k_, d_ in (('dim', .5), ('glow', 1.0), ('edge', 1.0), ('line', 1.0), ('light_m', 45), ('halo_m', 14))},
    'wave_dur': FM.get('wave_dur', 3.2), 'dim': dim_keys, 'sky': sky_out, 'context': CTX_OUT,
    'change': {'renew': CHANGE['renew'], 'early': CHANGE.get('early', []), 'counts': CHANGE['counts']} if CHANGE else None,
    'rings_motif': ({'centre': F.model_lonlat(*FM['rings_motif']['centre']), 'spacing': FM['rings_motif'].get('spacing_m', 350) * F.scale, 'from': FM['rings_motif'].get('from', first_year), 'gain': FM['rings_motif'].get('gain', .5)} if FM.get('rings_motif') else None),
}
# pictures must not hide a change (SKILL.md 演出文法 5b; the user, 2026-10-21). Full-frame footage hides everything, so it never
# shows during one. A half-screen panel (engine/overlay.js: the right 64 % of the frame, melting in over 260 px) may show beside a
# city that grows or burns on the left of the frame; it may not cover more than a third of that place on screen, sampled four times
# a second. Changes across the whole frame (a node's colour ring, today's buildings rising, the satellite plate's sweeps, an area
# lighting up, the sky plan drawn over the city) count as covered. A small card may sit over any change.
PANEL_NDC = .36 * 2 - 1 + 130 / 960
def _hidden(t, c, r):   # share of a place's on-screen points (its centre and eight round its edge) under the panel at t
    pts = [c] + [(c[0] + r * math.cos(k * math.pi / 4), c[1], c[2] + r * math.sin(k * math.pi / 4)) for k in range(8)]
    q = [v for v in (CAMERA.project(t, p_) for p_ in pts) if v and abs(v[0]) <= 1 and abs(v[1]) <= 1]
    return sum(v[0] > PANEL_NDC for v in q) / len(q) if q else 0.0
def _changes():   # (t0, t1, what, places or None for the whole frame)
    for n in nodes_out: yield n.get('arrive', n['t0']), n.get('arrive', n['t0']) + film['wave_dur'], f"{n['id']}'s colour ring", None
    for era_, (a_, b_), c_, r_, _ in PLACES: yield a_, b_, f'era {era_} growing', [(c_, r_)]
    for e in eras_out:
        if e.get('off'): yield (e['off'] - (e.get('burn') or 0), e['off'] + e.get('sink', 2.5), f"era {e['id']} {'burning and ' if e.get('burn') else ''}going",
                                [(c_, r_) for era_, _, c_, r_, _ in PLACES if era_ == e['id']] or None)
    for ep in epochs: yield ep['on'], ep['on'] + (ep.get('fade') or 1), f"area {ep['id']} lighting up", None
    for b in (grow or {}).get('bands', []): yield b['t'] - b['spread'] / 2, b['t'] + b['spread'] / 2, f"today's buildings of band {b['band']} rising", None
    if film.get('sky'): yield film['sky']['on'], film['sky']['off'], 'the sky plan', None
    s_ = film['satellite'] or {}
    if s_: yield s_['on'], s_['on'] + s_['fade'], 'the satellite plate sweeping in', None
    if s_.get('back'): yield s_['back'], s_['back'] + s_['backFade'], 'the satellite plate sweeping out', None
def _covers(x):   # the changes a picture hides while it is fully up: [(from, to, what)]
    m_ = x.get('mode', 'full'); x0_, x1_ = x['on'] + x.get('fin', 1.0), x['on'] + x['dur'] - x.get('fout', 1.0)   # (the fades leave the map seen)
    out_ = []
    for a, b, w, places_ in _changes():
        if not (a < x1_ and b > x0_): continue
        if m_ == 'panel' and places_:
            ts_ = [max(a, x0_) + k * .25 for k in range(int((min(b, x1_) - max(a, x0_)) / .25) + 1)]
            worst_ = max(_hidden(t_, c_, r_) for t_ in ts_ for c_, r_ in places_)
            if worst_ <= 1 / 3: continue
            w = f'{w}, {worst_:.0%} of it under the panel'
        out_.append((a, b, w))
    return out_
_cover = []
for x in footage_out:
    m_ = x.get('mode', 'full')
    if m_ not in ('panel', 'full'): continue
    hits_ = _covers(x)
    if not hits_: continue
    say_ = lambda h_: f"{x['id']} ({m_}, {x['on']:.1f}-{x['on'] + x['dur']:.1f} s) over {h_[2]} ({h_[0]:.1f}-{h_[1]:.1f} s)"
    if x['force']:   # (the author says hiding it does not matter)
        print('  note: ' + '; '.join(say_(h_) for h_ in hits_) + ': shown anyway (force)'); continue
    if m_ == 'panel':   # a panel waits until the change is over, but not past its line (the one it follows, else the one it came with)
        on0_ = x['on']; ln_ = x['_with'] or max((c for c in cues if c['node'] == x['_node'] and c['t0'] <= on0_ + .05), key=lambda c: c['t0'], default={}).get('id')
        cue_ = next((c for c in cues if c['id'] == ln_), None)
        for _ in range(6):
            hits_ = _covers(x)
            if not hits_: break
            x['on'] = round(max(h_[1] for h_ in hits_) - x.get('fin', 1.0) + .3, 3)
        if not hits_ and cue_ is not None and x['on'] + x.get('fin', 1.0) <= cue_['t1'] - 1.0:
            print(f"  picture {x['id']}: {x['on'] - on0_:+.1f} s, after the change it would hide (still with {ln_})"); continue
        x['on'] = on0_; hits_ = _covers(x)
        _cover.append(say_(hits_[0]) + f' (moved past the change it would leave {ln_ or "its line"})')
        continue
    _cover += [say_(h_) for h_ in hits_]
if _cover: raise SystemExit('compile: a picture hides a change (SKILL.md 演出文法 5b: compose the shot so the change is on the left, move the '
                           'picture to another line, make it a card, or give it force: true if hiding that change does not matter): ' + '; '.join(_cover))
# the film's type (SKILL.md 演出文法 10b): one font per job, by family name and weight (film.fonts), looked up in <root>/fonts
# (pipeline/fonts.py); a family or weight that is not there, or a character of the copy a font cannot draw, stops the build: the
# browser would draw it in a system font (one subtitle line in two weights, as once happened)
import fonts as FONTS
FONT_ROLES = {'primary_strong': 'first language: headings and subtitles, tags, place names', 'primary': 'first language: readout labels, small text',
              'primary_sans': 'first language, sans: end-card lines', 'primary_sans_strong': 'first language, sans, strong: the sky plan labels',
              'numeral': 'big numerals: years, counts, the title in Latin letters', 'numeral_strong': 'the timeline year, measured heights',
              'secondary': 'second language: subtitles and captions', 'secondary_strong': 'second language under tags and labels, measurements',
              'mono': 'notes, credits, small caps lines'}
OLD_ROLE = {'zh_strong': 'primary_strong', 'zh': 'primary', 'zh_sans': 'primary_sans', 'zh_sans_strong': 'primary_sans_strong', 'en': 'secondary', 'en_strong': 'secondary_strong'}
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg = {OLD_ROLE.get(k_, k_): v_ for k_, v_ in (FM.get('fonts') or {}).items()}   # (the older names, zh_* and en*, still read)
_miss_roles = [r_ for r_ in FONT_ROLES if r_ not in _cfg]
if _miss_roles: raise SystemExit('compile: film.fonts needs a font for every job: ' + '; '.join(f'{r_} ({FONT_ROLES[r_]})' for r_ in _miss_roles) + ' (see templates/city.yaml)')
_idx = FONTS.index(_ROOT); _alias = {}; faces_ = []; roles_ = {}
_text = json.dumps(film, ensure_ascii=False)
_cjk = set(re.findall(r'[\u3000-\u303F\u3040-\u30FF\u3400-\u9FFF\uF900-\uFAFF\uFF00-\uFFEF\uAC00-\uD7AF]', _text)); _ascii = {chr(c) for c in range(32, 127)}
_latin = set(re.findall(r'[\u00C0-\u024F]', _text))
_other = {c for c in _text if ord(c) > 127 and c not in _cjk and c not in _latin and c.isprintable()}
_needs = lambda sc_: _ascii | (_cjk if sc_ in ('cjk', 'hangul') else _latin)   # (a language's face draws its own script and the digits)
for r_, v_ in _cfg.items():
    if r_ not in FONT_ROLES: raise SystemExit(f'compile: film.fonts.{r_}: no such job (jobs: {", ".join(FONT_ROLES)})')
    fam_, wt_ = v_['family'], int(v_.get('weight', 400))
    face_ = FONTS.find(_idx, fam_, wt_)
    if face_['file'] not in _alias:
        _alias[face_['file']] = f'F{len(_alias)}'
        faces_.append({'alias': _alias[face_['file']], 'file': 'fonts/' + face_['file'], 'weight': f'{face_["wmin"]:.0f} {face_["wmax"]:.0f}' if face_['wmin'] != face_['wmax'] else f'{face_["wmin"]:.0f}', 'family': fam_})
    roles_[r_] = f'{wt_} {{}}px {_alias[face_["file"]]}'
    need_ = _needs(SCRIPTS[0]) if r_.startswith('primary') else _needs(SCRIPTS[-1]) if r_.startswith('secondary') else _ascii
    lack_ = FONTS.missing(_ROOT, face_, need_)
    if lack_: raise SystemExit(f'compile: film.fonts.{r_} ({fam_}) has no glyph for {"".join(lack_[:40])}: the browser would draw them in a system font; pick a font that has them')
    soft_ = FONTS.missing(_ROOT, face_, _other)
    if soft_ and r_.startswith('primary'): print(f'  fonts: {r_} ({fam_}) lacks {"".join(soft_)} (symbols; only a problem if this job draws them)')
roles_.update({o_: roles_[n_] for o_, n_ in OLD_ROLE.items()})   # (the engine's older names draw with the same faces)
film['fonts'] = {'faces': faces_, 'roles': roles_}
print('  fonts: ' + ', '.join(f'{r_} {_cfg[r_]["family"]} {_cfg[r_].get("weight", 400)}' for r_ in FONT_ROLES))
# the film's languages on screen (engine: overlay setUI, main yearAs): how a year is written, the program's own words, the subtitle type
_ypack = FM.get('yearFmt') if FM.get('yearFmt') in _LANGS_ANY and os.path.exists(os.path.join(i18n.ROOT, 'i18n', f"{FM.get('yearFmt')}.yaml")) else LANG[0]
film['years'] = i18n.pack(_ypack)['year']
_ui_l = next((l_ for l_, sc_ in zip(LANG, SCRIPTS) if sc_ == 'latin'), LANG[0])   # (chapter and locator words in capitals: a Latin-script language when there is one)
film['ui'] = {'chapter': i18n.word(_ui_l, 'chapter'), 'locator': i18n.word(_ui_l, 'locator')}
_px = lambda sc_, first: (38 if sc_ in ('cjk', 'hangul') else 34) if first else (32 if sc_ in ('cjk', 'hangul') else 30)
film['sub'] = {'a': ['zh_strong', _px(SCRIPTS[0], True)], 'b': ['en', _px(SCRIPTS[-1], False)]}
if MISSING:
    _m = list(dict.fromkeys(MISSING))
    raise SystemExit(f'compile: {len(_m)} text(s) on screen have no {", ".join(sorted({l_ for l_, _ in _m}))} version (film.lang {LANG}): ' + '; '.join(f'{l_}: {w_}' for l_, w_ in _m[:12]))
# the silences meant to be there: script.yaml quiet stretches and pauses (film seconds)
_quiet = []
for nid_, rs_ in ((SCR or {}).get('quiet') or {}).items():
    nd_ = next((n for n in FM['nodes'] if n['id'] == nid_), None)
    if nd_ is None: raise SystemExit(f'script.yaml quiet: no node {nid_!r}')
    _quiet += [(node_time(nd_, r_[0]), node_time(nd_, r_[1])) for r_ in rs_]
_declared = list(_quiet) + [q_ for n_ in FM['nodes'] for q_ in n_.get('_pauses', [])]
# the narration as one track for the live preview (engine: heard while playing, kept in step with the picture; the user,
# 2026-10-22): every voiced line laid at its time, 48 kHz mono, build/audio/voice/track_<lang>.wav (the mix reads the lines)
_voiced = [c_ for c_ in cues if voice_len(c_['id'])]
if _voiced:
    import subprocess, wave
    import numpy as np
    _sr = 48000; _trk = np.zeros(int((DUR + 1) * _sr), np.int32)
    for c_ in _voiced:
        f_ = next(os.path.join(VOICE_DIR, f"{c_['id']}.{e_}") for e_ in ('wav', 'mp3', 'm4a', 'ogg', 'flac') if os.path.exists(os.path.join(VOICE_DIR, f"{c_['id']}.{e_}")))
        x_ = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f_, '-f', 's16le', '-ac', '1', '-ar', str(_sr), '-'], capture_output=True, check=True).stdout, np.int16)
        a_ = int(c_['t0'] * _sr); x_ = x_[:max(0, len(_trk) - a_)]; _trk[a_:a_ + len(x_)] += x_
    _vf = os.path.join(D, 'build', 'audio', 'voice', f'track_{VOICE_LANG}.wav')
    with wave.open(_vf, 'wb') as w_: w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(_sr); w_.writeframes(np.clip(_trk, -32768, 32767).astype(np.int16).tobytes())
    _vm = _vf[:-4] + '.m4a'   # (what the preview loads whole: the preview server answers no range requests, so a 70 MB WAV seeked badly)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', _vf, '-c:a', 'aac', '-b:a', '128k', _vm], check=True)
    film['voice'] = {'lang': VOICE_LANG, 'file': os.path.relpath(_vm, os.path.join(D, 'build')), 'lines': len(_voiced)}
    print(f'  voice: {len(_voiced)} of {len(cues)} lines voiced ({VOICE_LANG}), the preview plays {film["voice"]["file"]}')
# the score laid on the timeline (audio/lay.py; the city's MUSIC.md), dipped under the voice: film.music.source cues, each cue from
# its node; or code, the code score audio/codescore.py wrote. The preview plays it beside the narration (B mutes it), the mix lays its WAV
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio'))
import lay as LAY
_msrc = (FM.get('music') or {}).get('source', 'cues')
if _msrc not in ('cues', 'code'): raise SystemExit(f'film.music.source: cues (laid by node) or code (audio/codescore.py), not {_msrc!r}')
_vspans = [(c_['t0'], c_['t0'] + voice_len(c_['id'])) for c_ in _voiced]
_vwav = os.path.join(D, 'build', 'audio', 'voice', f'track_{VOICE_LANG}.wav') if _voiced else None
_score = (LAY.lay_code(D, FM.get('music'), DUR, _vspans, _declared, _vwav, LAY.timing(film)) if _msrc == 'code'
          else LAY.lay(D, FM.get('music'), {n_['id']: n_['t0'] for n_ in nodes_out}, DUR, _vspans, _declared, _vwav))
# the sound effects kept beside the score (city.yaml film.sfx; the user, 2026-10-22), at the moments the page fires them (main.js
# ev(): the relay as the lights go out, the lamp, each burning era from its off less its burn, the lights at the end)
if FM.get('sfx'):
    _ev = [(light['lightsOut'], 'relay'), (light['lamp'], 'lamp'), (light['lights'], 'lights')] if light.get('lights') else [(light['lightsOut'], 'relay'), (light['lamp'], 'lamp')]
    _ev += sorted({(round(e_['off'] - e_['burn'], 3), 'burn') for e_ in film.get('eras', []) if e_.get('sinkStyle') == 'burn' and e_.get('off') is not None})
    film['sfx'] = LAY.lay_sfx(D, FM['sfx'], [q_ for q_ in _ev if q_[1] in FM['sfx']], DUR, _vspans, _vwav,
                                  os.path.join(D, 'build', 'audio', 'music', 'score.wav') if _score and _score['file'] else None)
    print(f"  sfx: {', '.join(FM['sfx'])}" + (f" laid at {', '.join(f'{t_:.2f}' for t_, _ in film['sfx']['events'])}" if film['sfx']['file'] else ' (no one-shots yet: python -I audio/mix.py <city> --kit, then compile again)'))
if _score:
    if _score['file']: film['score'] = _score
    print(("  music: the code score " + ('laid' if _score['file'] else f'not written yet: python -I audio/codescore.py {D} (after render/events.mjs)') if _msrc == 'code' else
           f"  music: {len(_score['cues']) - len(_score['missing'])} of {len(_score['cues'])} cues laid" + (f", no take yet: {' '.join(_score['missing'])}" if _score['missing'] else ''))
          + ''.join('; ' + n_ for n_ in _score.get('notes', [])))
json.dump(film, open(LAYOUT.build(D, 'film.json'), 'w'), ensure_ascii=False, indent=1)
# the words on the final timeline, written out (subtitles in every language, the timed script for voice work: pipeline/subtitles.py)
import subtitles as SUBS
SUBS.write(LAYOUT.export(D), os.path.basename(D), cues, LANG, hold, end_t)
# the copy check (pipeline/copylint.py): where words are missing, too many, or off the house style; advice, written to build/logs
import copylint as COPY
_finds = COPY.check(film, FM.get('copy'), _quiet, LANG[0])
# dead air (SKILL.md 演出文法 5c): (a) a stretch longer than dead_air_s with no line spoken, nothing changing on the model, no picture
# up and the camera all but still; (b) a gap between two lines longer than word_gap_s that nothing declares (a quiet stretch or a
# pause), no full-screen clip fills, and that is not the next line waiting for its picture while the picture moves (the next line
# is its node's first, or follows a picture: with). The planner's holds made (b) (秦都 50-57 s, 2026-10-21)
_LINE = {c_['id']: c_ for n_ in FM['nodes'] for c_ in n_.get('cues', []) if 'id' in c_}
_FIRST = {next((c_['id'] for c_ in n_.get('cues', []) if 'id' in c_), None) for n_ in FM['nodes']}
_pict = [(x['on'], x['on'] + x['dur']) for x in footage_out]
_pict += [(a_, b_) for a_, b_, w_, _ in _changes() if 'growing' not in w_] + [(a_, b_) for _, _, _, _, (a_, b_) in PLACES]   # (a city: while its buildings rise)
_pict += [(r['on'], r['on'] + r.get('draw', 0) + .5) for r in routes_out]
_pict += [(q['on'], q['on'] + (q.get('fade') or 1)) for q in lines] + [(q['on'], q['on'] + (q.get('fade') or 1)) for q in decals_out]
_pict += [(p_['t0'], p_['t0'] + 1.0) for p_ in pins] + [(s_['t0'], s_['t1']) for s_ in sections]   # (a terrain section: a panel, as a photo)
def _moving(t, step=.25):   # the picture moves: something changes, a picture is up, or the camera travels
    if any(a_ - 1e-6 <= t <= b_ for a_, b_ in _pict): return True
    gt_ = globals().get('GROW_T') or []
    if gt_:
        import bisect
        if bisect.bisect_right(gt_, t) - bisect.bisect_left(gt_, t - 1.8) >= 5: return True   # buildings rising here
    p0, g0, f0, d0 = CAMERA.at(t); p1, g1, f1, d1 = CAMERA.at(t + step)
    return math.dist(p0, p1) / step > .04 * d0 or math.dist(g0, g1) / step > .04 * d0 or abs(f1 - f0) / step > .5
def _dead_air():
    spoken_ = [(c['t0'], c['t1'] + .3) for c in cues] + _declared
    t, step, hi = light['lamp'], .25, end['t']; runs, s_ = [], None
    while t <= hi:
        b_ = any(a_ - 1e-6 <= t <= b_ for a_, b_ in spoken_) or _moving(t)
        if not b_ and s_ is None: s_ = t
        if b_ and s_ is not None:
            if t - s_ > TIMING['dead_air_s']: runs.append((s_, t))
            s_ = None
        t += step
    if s_ is not None and hi - s_ > TIMING['dead_air_s']: runs.append((s_, hi))
    out = []
    for a_, b_ in runs:
        nd_ = next((n for n in nodes_out if n['t0'] <= a_ < n['t1']), None)
        prv = max((c for c in cues if c['t1'] <= a_ + .3), key=lambda c: c['t1'], default=None); nxt = min((c for c in cues if c['t0'] >= b_ - .3), key=lambda c: c['t0'], default=None)
        out.append(f"nothing at all {a_:7.2f}-{b_:7.2f} s ({b_ - a_:.1f} s) in {nd_['id'] if nd_ else '-'}: after {prv['id'] if prv else '-'}, before {nxt['id'] if nxt else '-'}")
    for c_, n_ in zip(cues, cues[1:]):   # (b)
        g0_, g1_ = c_['t1'], n_['t0']; L_ = g1_ - g0_
        if L_ <= TIMING['word_gap_s']: continue
        # what fills it: a declared silence, any picture with its caption (footage, photos, cards, a terrain section), the flight to a new node
        fill_ = [(a_, b_) for a_, b_ in _declared] + [(x['on'], x['on'] + x['dur']) for x in footage_out] + [(s_['t0'], s_['t1']) for s_ in sections]
        nd_ = next((n for n in nodes_out if n['t0'] <= g1_ - .01 < n['t1']), None)
        if n_['id'] in _FIRST and nd_: fill_.append((nd_['t0'], nd_['arrive']))   # (the picture travels; the first line comes on arrival)
        open_ = sum(1 for k_ in range(int(L_ / .25)) if not any(a_ <= g0_ + k_ * .25 <= b_ for a_, b_ in fill_)) * .25
        if open_ <= TIMING['word_gap_s']: continue
        mov_ = sum(1 for k_ in range(int(L_ / .25)) if _moving(g0_ + k_ * .25)) * .25
        why_ = ('waits for ' + _LINE[n_['id']]['with']) if 'with' in _LINE.get(n_['id'], {}) else ('waits for the picture clock (t)' if 't' in _LINE.get(n_['id'], {}) else
                'the node before runs on after its last line' if n_['id'] in _FIRST else 'after a pause')
        out.append(f"no words      {g0_:7.2f}-{g1_:7.2f} s ({L_:.1f} s, {open_:.1f} s with nothing to read) {c_['id']} -> {n_['id']}: {why_} (moving {mov_:.1f} s)")
    return out
_dead = _dead_air()
open(LAYOUT.logs(D, 'deadair.txt'), 'w', encoding='utf-8').write('\n'.join(_dead) + '\n')
print(f'  dead air: {len(_dead)} stretch(es)' + ''.join('\n    ' + d_ for d_ in _dead))
if _dead and os.environ.get('CT_DEADAIR') != 'warn':   # (CT_DEADAIR=warn: report only, while a city is being written)
    raise SystemExit(f'compile: dead air (SKILL.md 演出文法 5c; build/logs/deadair.txt): let a line follow the one before, have it wait for the '
                     f'picture it speaks of (with:), shorten the hold, or declare a pause: ' + '; '.join(_dead))
# the timeline for voice, music and sound (design phase 4): every line, every change on the model, the pictures over it, the
# silences meant to be there, and each node's feeling; seconds of the final film (build/export/timeline.json)
_tl = {'dur': DUR, 'langs': LANG, 'voice': {'lang': VOICE_LANG, 'dir': os.path.relpath(VOICE_DIR, D)},
       'emblem': EMBLEM,
       'nodes': [{'id': n_['id'], 't0': n_['t0'], 't1': n_['t1'], 'arrive': n_['arrive'], 'years': n_['years'], 'label': n_['label'], 'mood': n_['mood']} for n_ in nodes_out],
       'lines': [{'id': c_['id'], 'node': c_.get('node'), 't0': c_['t0'], 't1': c_['t1'], 'text': dict(zip(LANG, [c_.get('a'), c_.get('b')])),
                  'voice': voice_len(c_['id'])} for c_ in cues],
       'changes': sorted([{'t0': round(a_, 3), 't1': round(b_, 3), 'what': w_} for a_, b_, w_, _ in _changes()], key=lambda q: q['t0']),
       'pictures': [{'id': x['id'], 'mode': x.get('mode', 'full'), 't0': x['on'], 't1': round(x['on'] + x['dur'], 3), 'title': x.get('title')} for x in footage_out],
       'silences': [{'t0': round(a_, 3), 't1': round(b_, 3)} for a_, b_ in _declared],
       'lights': {'on': light['lamp'], 'off': light.get('lights'), 'end_card': end_t}}
json.dump(_tl, open(os.path.join(LAYOUT.export(D), 'timeline.json'), 'w'), ensure_ascii=False, indent=1)
print('  arc: ' + ' '.join(f"{n_['id']}:{n_['mood']['feel']}{n_['mood']['level']}" for n_ in nodes_out))
open(LAYOUT.logs(D, 'copy.txt'), 'w', encoding='utf-8').write(COPY.report(_finds))
_kinds = {k_: sum(1 for f_ in _finds if f_[2] == k_) for k_ in ('add', 'cut', 'style', 'check')}
print('  copy: ' + ', '.join(f'{v_} {k_}' for k_, v_ in _kinds.items()) + f' (advice: {os.path.relpath(LAYOUT.logs(D, "copy.txt"))})')
print(f'film.json: {DUR}s from {len(nodes_out)} nodes; {len(epochs)} epochs, {len(lines)} line groups, {len(decals_out)} decals, {len(props_out)} props, {len(tally_keys)} tally keys, {len(pins)} pins, {len(cues)} cues, {len(readouts)} readouts, camera keys {len(cam)}')
for nd in nodes_out: print(f'  node {nd["id"]:12s} {nd["t0"]:7.2f}-{nd["t1"]:7.2f}  {nd["years"][0]:.0f} → {nd["years"][1]:.0f}  {nd["label"]}')
# keys of city.yaml nothing read (Seen): compile and the modules it hands the settings to have read theirs by now; the steps that
# read city.yaml themselves (prep.py, terrain.py, tools/music.py, ...) name their keys in quotes in their code
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_theirs = set()
for d_ in ('pipeline', 'tools', 'audio', 'render'):
    for f_ in sorted(os.listdir(os.path.join(_ROOT, d_))):
        if not f_.endswith(('.py', '.mjs', '.js')) or f_ == 'compile.py': continue
        s_ = open(os.path.join(_ROOT, d_, f_), encoding='utf-8').read()
        if 'city.yaml' in s_ and re.search(r'safe_load|yaml\.load|YAML\.parse', s_): _theirs |= set(re.findall(r'''['"]([A-Za-z_][\w-]*)['"]''', s_))
def _unread(o, path=''):
    if isinstance(o, Seen):
        for k in [k_ for k_ in dict.keys(o) if k_ in getattr(o, 'mine', ())]:
            p_ = f'{path}.{k}' if path else str(k)
            if k not in o.read and str(k) not in _theirs: yield p_
            elif k in o.read: yield from _unread(dict.__getitem__(o, k), p_)
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from _unread(v, f'{path}[{dict.get(v, "id", i) if isinstance(v, dict) else i}]')
_nobody = list(_unread(C))
if _nobody: WARN.append('city.yaml keys nothing reads (a typo, a key in the wrong place, or one this version does not have): ' + ', '.join(_nobody))
for w_ in WARN: print('warning: ' + w_, file=sys.stderr)
