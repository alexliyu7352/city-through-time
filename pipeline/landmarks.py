"""Landmarks of any region and period, as data (docs/MODEL.md "Landmarks of any region"). A landmark names a class of massing (`kind`) and gives
its sizes in metres from the research; the classes cover the monuments of most traditions (amphitheatres and theatres, domed
buildings, long halls from temples to cathedrals, towers from obelisks to minarets and pagodas, stepped platforms and pyramids,
rows of arches), two free solids take any other form (a section turned round an axis, an outline carried straight), and `parts`
puts several together (a domed hall with its portico, a cathedral with its towers, a mosque with its minarets).

check() completes a landmark with its defaults and stops compile with what to write: a key the kind does not have, a value out
of range, a missing size or a missing basis. build() draws it with citygen's Builder. The table of every kind's keys (FIELDS)
is the one source of what can be written; print it with

    uv run python -I pipeline/landmarks.py [kind]
"""
import math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import citygen as C

REQ = object()   # a field's default: required


class Bad(Exception):
    pass


# ------------------------------------------------------------------ the fields of every kind
# a field: (type, range or choices or sub-fields, default, what it is). Types: num, int, enum, bool, pair ([a, b] in metres, or
# one number for both), pts ([[x, y], ...]), rings (a list of pts), obj (sub-fields), list (a list of obj), str, ll ([lon, lat]).
# Default REQ: required; None: optional, worked out from the others when absent.
SHAPES = ('hemisphere', 'saucer', 'pointed', 'onion', 'bulbous', 'helmet', 'bell', 'cone')
ROOFS = ('gabled', 'hipped', 'hip_gable', 'pyramidal', 'flat', 'vault', 'mansard')
SECTIONS = ('round', 'square', 'octagon', 'hexagon', 'rect')
TOPS = ('flat', 'pyramid', 'cone', 'spire', 'dome', 'onion', 'bulbous', 'helmet', 'statue', 'lantern', 'shikhara')

COMMON = {
    'kind': ('str', None, REQ, 'the class of massing (below)'),
    'lon': ('num', (-180, 180), None, 'the centre (with lat); a run of arches may give from and to instead'),
    'lat': ('num', (-90, 90), None, 'the centre'),
    'theta_deg': ('num', (-360, 360), None, 'its turn, counter-clockwise from east: at 0 its x runs east and its front faces south (the city\'s theta_deg when absent)'),
    'basis': ('str', None, REQ, 'where the sizes come from (a research note) and which of them are estimates'),
    'name': ('str', None, None, 'what it is (messages, the sheet)'),
    'id': ('str', None, None, 'its name for a stage to select it by (stages name parts by id or group, never by index)'),
    'group': ('str', None, None, 'a name it shares with the others a stage selects together'),
    'exaggeration': ('num', (.5, 5), None, 'its heights\' exaggeration (when absent the city\'s, fading as the landmark gets taller: see exaggeration(); 1: true, for one drawn after a true elevation)'),
    'z_m': ('num', (0, 300), 0.0, 'metres above its ground (a part standing on another: a dome on a hall\'s crossing)'),
}
PART = {   # what a part of `parts` adds
    'at': ('pair', (-2000, 2000), None, '[x, y] metres from the whole\'s centre, in its frame (x along it, y to its back)'),
    'atop': ('int', (0, 50), None, 'stands on the top of that part (its index in parts, an earlier one), z_m above it: a lantern on a dome, a spire on a tower (a dome keeps its true curve while other heights are exaggerated, so a z_m counted by hand misses its top)'),
    'repeat': ('obj', {
        'mirror': ('enum', ('x', 'y', 'xy'), None, 'also its mirror image across the whole\'s x axis (y: its y axis; xy: both, four in all)'),
        'ring': ('obj', {'n': ('int', (2, 200), REQ, 'how many'), 'r_m': ('num', (0, 2000), REQ, 'round the whole\'s centre at this radius (at is ignored)'),
                         'start_deg': ('num', (-360, 360), 0.0, 'where the first stands, counter-clockwise from the frame\'s x')}, None, 'n copies on a circle, each turned to face out'),
        'line': ('obj', {'n': ('int', (2, 400), REQ, 'how many'), 'step_m': ('pair', (-2000, 2000), REQ, '[dx, dy] metres from one to the next')}, None, 'n copies in a row from at'),
        'corners': ('pair', (0, 2000), None, '[w, d]: one at each corner of a w x d rectangle round the whole\'s centre (at is ignored)'),
    }, None, 'copies of this part (corner minarets, a ring of chapels, pinnacles in a row)'),
}
FIELDS = {
    'ring': ({
        'plan': ('enum', ('oval', 'round', 'obround', 'u', 'half'), 'oval', 'oval or round (an amphitheatre, a stadium, a round house like a tulou); obround: straight sides between two round ends; u: one round end and a straight one (a circus, a Greek stadium); half: a part of a circle round an orchestra (a theatre)'),
        'outer_m': ('pair', (5, 1500), REQ, '[length along x, width along y] of the outer wall; one number when round (half: the diameter)'),
        'inner_m': ('pair', (0, 1400), REQ, '[length, width] of the open floor (arena, orchestra, track); the band between keeps the depth its width gives, so the floor\'s length follows from it'),
        'h_m': ('num', (1, 100), REQ, 'height of the outer wall'),
        'section': ('enum', ('seats', 'building'), 'seats', 'seats: tiers falling from the top of the outer wall to the floor; building: a ring of rooms with walls the same height inside and out'),
        'arena_wall_m': ('num', (0, 30), 4.0, 'seats: the wall round the floor (the podium)'),
        'roof': ('enum', ('flat', 'pitched'), 'flat', 'building: its roof'),
        'storeys': ('int', (0, 8), 0, 'rows of arched openings on the outer wall (an amphitheatre\'s arcades); 0: a plain wall'),
        'bays': ('int', (4, 400), None, 'openings in each row (one every 7 m round when absent)'),
        'sweep_deg': ('num', (60, 360), 180.0, 'half: how much of a circle the seats turn (a Greek theatre a little more than half)'),
        'stage': ('obj', {'d_m': ('num', (1, 80), 10.0, 'its depth'), 'h_m': ('num', (1, 100), None, 'its height (the seats\' when absent: a Roman stage wall)')}, None, 'half: the stage building closing the open side'),
        'spina': ('obj', {'share': ('num', (.2, .95), .6, 'its length as a share of the straight part'), 'w_m': ('num', (1, 40), 8.0, 'its width'), 'h_m': ('num', (.5, 20), 3.0, 'its height')}, None, 'u, obround: the barrier down the middle of a circus'),
    }, 'a ring of seats or rooms round an open floor: amphitheatres, theatres, circuses and stadia, round houses'),
    'dome': ({
        'd_m': ('num', (1, 250), REQ, 'outer diameter of the drum (the wall the dome stands on)'),
        'sides': ('int', (0, 32), 0, '0: round; 8: an octagon (Florence), 4: square, any other polygon'),
        'base': ('obj', {'w_m': ('num', (1, 400), REQ, 'its width'), 'd_m': ('num', (1, 400), None, 'its depth (its width when absent)'), 'h_m': ('num', (.3, 150), REQ, 'its height')}, None, 'a block under it: a square chamber, a podium'),
        'drum_h_m': ('num', (0, 200), 0.0, 'height of the drum (a rotunda\'s wall); 0: the dome sits on the base or the ground'),
        'dome': ('obj', {
            'shape': ('enum', SHAPES, 'hemisphere', 'its profile: hemisphere; saucer (lower than half, Hagia Sophia); pointed (Florence, Timurid); onion (Russian, wider than its drum, a point on top); bulbous (Mughal); helmet; bell (a stupa, a chedi); cone'),
            'rise_m': ('num', (.3, 250), None, 'its height from where it springs (by shape when absent: hemisphere half its width, saucer a quarter, pointed .74, onion one width, bulbous .9, helmet .7, bell one, cone .8)'),
            'd_m': ('num', (1, 300), None, 'its own width (an onion or a bulbous dome is wider than its drum: the drum\'s width over .7 or .8 when absent; others the drum\'s)'),
            'keep_curve': ('bool', None, True, 'its curve kept true while the walls are exaggerated (stretched, a dome reads as an egg)'),
        }, {}, 'the dome'),
        'lantern': ('obj', {'d_m': ('num', (.5, 40), REQ, 'its width'), 'h_m': ('num', (.5, 60), REQ, 'its height'), 'top': ('enum', ('dome', 'cone', 'onion', 'point'), 'dome', 'its cap')}, None, 'a small turret on top'),
        'finial_m': ('num', (0, 40), 0.0, 'a mast on top (a cross, a crescent, a kalasha)'),
        'oculus_m': ('num', (0, 60), 0.0, 'a dark round opening at the top (the Pantheon\'s 9 m)'),
        'sweep_deg': ('num', (60, 360), 360.0, '180: a half dome, its open side to the front (against a bigger dome or a hall)'),
        'peristyle': ('obj', {'n': ('int', (4, 120), REQ, 'columns'), 'h_m': ('num', (1, 120), None, 'their height (the drum\'s when absent)'), 'gap_m': ('num', (.5, 30), 3.0, 'from the drum to the columns\' line'), 'col_m': ('num', (.2, 5), .9, 'a column\'s thickness')}, None, 'a ring of columns round the drum (a tholos, St Peter\'s drum)'),
    }, 'a round or polygonal building under a dome: rotundas, mausoleums, domed mosques and churches, stupas, baptisteries'),
    'long_hall': ({
        'w_m': ('num', (2, 400), REQ, 'its width, across the front (with its aisles and colonnade)'),
        'd_m': ('num', (2, 800), REQ, 'its length, front to back'),
        'h_m': ('num', (1, 120), REQ, 'height of its walls to the eaves (the nave\'s, with aisles)'),
        'roof': ('obj', {
            'shape': ('enum', ROOFS, 'gabled', 'gabled (a pediment at each end), hipped, hip_gable (hipped below, gabled above), pyramidal, flat, vault (a barrel), mansard'),
            'pitch_deg': ('num', (3, 75), None, 'its slope (gabled 22, hipped 25, hip_gable 28, pyramidal 30, mansard 70 for its steep part when absent; a Greek temple about 15)'),
            'overhang_m': ('num', (0, 8), None, 'eaves past the walls (.6 when absent; flared East Asian eaves more)'),
            'eaves': ('int', (1, 4), 1, 'tiers of eaves (East Asian double eaves: 2)'),
            'flared': ('bool', None, False, 'East Asian roof: upturned eaves, a heavy ridge (gabled, hipped, hip_gable)'),
            'rise': ('num', (.1, 1.2), .5, 'vault: its rise over its span (.5 a half circle, more: pointed)'),
        }, {}, 'its roof (over the nave; aisles get lean-to roofs)'),
        'aisles': ('obj', {'n': ('int', (1, 3), 1, 'aisles on each side'), 'w_m': ('num', (1, 60), REQ, 'each aisle\'s width'), 'h_m': ('num', (1, 100), REQ, 'height of their walls')}, None, 'lower side aisles under lean-to roofs, the nave rising above them (a basilica, a church)'),
        'apse': ('obj', {'at': ('enum', ('back', 'front', 'both'), 'back', 'which end'), 'r_m': ('num', (1, 100), None, 'its radius (half the nave\'s width when absent)'), 'h_m': ('num', (1, 120), None, 'its wall (the nave\'s when absent)')}, None, 'a half round end under a half dome'),
        'transept': ('obj', {'span_m': ('num', (2, 400), REQ, 'its length across'), 'w_m': ('num', (2, 200), None, 'its width (the nave\'s when absent)'), 'at': ('num', (0, 1), .72, 'where it crosses, a share of the length from the front'), 'h_m': ('num', (1, 120), None, 'its walls (the nave\'s when absent)')}, None, 'an arm across (a cross plan)'),
        'colonnade': ('obj', {'at': ('enum', ('around', 'front', 'front_back'), 'around', 'round all four sides (a peripteral temple), the front (a portico, a stoa\'s long front), front and back'), 'n_front': ('int', (2, 40), 6, 'columns across the front'), 'h_m': ('num', (1, 120), None, 'their height (the walls\' when absent)'), 'depth_m': ('num', (1, 40), None, 'from the columns to the wall behind (a portico two bays deep when absent)')}, None, 'columns under the roof\'s edge'),
        'podium': ('obj', {'h_m': ('num', (.2, 30), REQ, 'its height'), 'stair': ('enum', ('front', 'around', 'none'), 'front', 'front: one flight (a Roman temple); around: steps all round (a Greek temple\'s stylobate)')}, None, 'a platform under it'),
        'buttresses': ('obj', {'n': ('int', (2, 60), None, 'on each side (one every 7 m when absent)'), 'depth_m': ('num', (.5, 10), 2.5, 'how far each stands out'), 'flying': ('bool', None, False, 'flying buttresses over the aisles to the nave\'s wall (Gothic)')}, None, 'piers against the long walls'),
    }, 'a long rectangular hall under one roof: temples, basilicas, churches and cathedrals, stoas, market halls, prayer halls, palace halls'),
    'column': ({
        'section': ('enum', SECTIONS, 'round', 'its plan'),
        'sides': ('int', (3, 32), None, 'a polygon of this many sides (overrides section)'),
        'w_m': ('num', (.2, 150), None, 'its width at the foot (required without stages)'),
        'd_m': ('num', (.2, 150), None, 'rect: its depth'),
        'h_m': ('num', (.5, 700), None, 'its height without the top (required without stages)'),
        'taper': ('num', (0, 1), 1.0, 'its width at the top as a share of the foot (an obelisk .6, a lighthouse .63)'),
        'pedestal': ('obj', {'w_m': ('num', (.3, 200), REQ, 'its width'), 'd_m': ('num', (.3, 200), None, 'its depth (its width when absent)'), 'h_m': ('num', (.2, 100), REQ, 'its height')}, None, 'a block under it'),
        'stages': ('list', {
            'section': ('enum', SECTIONS, None, 'its plan (the column\'s when absent)'), 'sides': ('int', (3, 32), None, 'a polygon of this many sides'),
            'w_m': ('num', (.2, 150), REQ, 'its width at its foot'), 'd_m': ('num', (.2, 150), None, 'rect: its depth'), 'h_m': ('num', (.3, 300), REQ, 'its height'),
            'taper': ('num', (0, 1), 1.0, 'its top\'s width as a share of its foot'),
            'balcony_m': ('num', (0, 8), 0.0, 'a ledge round its top standing out this far (a minaret\'s balcony)'),
            'eave': ('obj', {'overhang_m': ('num', (.2, 12), REQ, 'how far it stands out'), 'h_m': ('num', (.2, 10), 1.5, 'its height')}, None, 'a roof skirt round its top (a pagoda\'s eave)'),
        }, None, 'sections stacked from the foot up (a minaret\'s shaft and balconies, a pagoda\'s storeys, a lighthouse\'s tiers); instead of w_m and h_m'),
        'top': ('obj', {'shape': ('enum', TOPS, 'flat', 'its crown'), 'h_m': ('num', (.2, 200), None, 'its height (by shape when absent)'), 'w_m': ('num', (.2, 150), None, 'its width (the shaft\'s top when absent)')}, {}, 'what crowns it'),
        'parapet': ('obj', {'h_m': ('num', (.3, 5), 1.2, 'merlon height'), 'merlon_m': ('num', (.3, 4), .9, 'merlon width (gaps the same)')}, None, 'battlements round its top (a castle tower)'),
    }, 'a tall shaft: obelisks, honorific columns, towers and keeps, minarets, bell towers, lighthouses, pagodas'),
    'stepped': ({
        'plan': ('enum', ('rect', 'round', 'polygon'), 'rect', 'its plan'),
        'sides': ('int', (3, 32), 8, 'polygon: its sides'),
        'w_m': ('num', (1, 1000), REQ, 'width at the foot'),
        'd_m': ('num', (1, 1000), None, 'rect: depth at the foot (its width when absent)'),
        'h_m': ('num', (.3, 300), REQ, 'height to the top platform'),
        'tiers': ('int', (1, 30), 3, 'how many (1 with top 0: a smooth pyramid)'),
        'top': ('num', (0, 1), .4, 'the top platform\'s width as a share of the foot (0: to a point)'),
        'slope': ('enum', ('battered', 'vertical'), 'battered', 'battered: each tier\'s face leans in (a ziggurat, a Mesoamerican pyramid); vertical: terraces with upright walls (Borobudur, an altar)'),
        'stair': ('obj', {'at': ('enum', ('front', 'all', 'none'), 'front', 'up the front, up all four sides, none'), 'w_m': ('num', (.5, 200), None, 'its width (.15 of the foot when absent)')}, {}, 'flights to the top'),
    }, 'a stepped platform or pyramid: pyramids, ziggurats, Mesoamerican temple platforms, altars, stupa terraces, temple mountains'),
    'arches': ({
        'from': ('ll', None, None, '[lon, lat] one end of a run (an aqueduct, a bridge, a loggia); with to, instead of lon, lat and length_m. Its top runs straight from end to end, h_m above the ground at each; over 120 m it is laid in pieces whose arches reach down to the ground under them'),
        'to': ('ll', None, None, '[lon, lat] the other end'),
        'length_m': ('num', (1, 5000), None, 'its length (with lon, lat)'),
        'h_m': ('num', (1, 120), REQ, 'height to its top'),
        'depth_m': ('num', (.3, 60), 3.0, 'its thickness'),
        'bays': ('int', (1, 600), None, 'arches in each tier (spans about as wide as a tier is high when absent)'),
        'tiers': ('int', (1, 5), 1, 'rows of arches one above the other (the Pont du Gard: 3)'),
        'arch': ('enum', ('round', 'pointed', 'flat', 'horseshoe'), 'round', 'the opening\'s head'),
        'opening': ('num', (.2, .92), .62, 'the opening\'s share of a bay\'s width (the rest is pier)'),
        'spring': ('num', (.15, .85), .5, 'where the arch springs, a share of the tier\'s height'),
        'attic_m': ('num', (0, 80), 0.0, 'a solid band above the arches (a triumphal arch\'s attic, an aqueduct\'s channel)'),
        'through': ('bool', None, True, 'false: the openings are deep recesses, dark at the back (an iwan, a pishtaq, a blind arcade)'),
        'recess_m': ('num', (.2, 40), None, 'not through: how deep (half the thickness when absent)'),
        'deck_m': ('num', (0, 60), 0.0, 'a deck on top this wide (a bridge\'s road)'),
    }, 'a wall of arches: triumphal arches, city gates, aqueducts and arched bridges, arcades and loggias, iwans and great portals'),
    'revolve': ({
        'profile_m': ('pts', 3, REQ, '[[r, y], ...] metres: a closed outline turned round the vertical axis, from the base round (r 0 on the axis, y 0 at the foot)'),
        'sides': ('int', (3, 128), 32, 'steps round (4: a square section, as a shikhara)'),
        'sweep_deg': ('num', (10, 360), 360.0, 'a part of a turn, centred on its back'),
        'oval': ('num', (.1, 10), 1.0, 'its depth over its width (1: round)'),
        'inset': ('bool', None, False, 'oval: r measured in from the outline along its normal (a band of one depth all round), not scaled'),
        'keep_curve': ('bool', None, False, 'its heights not exaggerated (a curve that must keep its shape)'),
    }, 'any solid turned round a vertical axis, from its section (a shape no class has)'),
    'prism': ({
        'plan_m': ('pts', 3, None, '[[x, y], ...] metres in its frame: an outline raised straight up (any plan: a star fort, a curved wall)'),
        'holes_m': ('rings', None, [], 'outlines cut out of the plan (a court, a cloister)'),
        'h_m': ('num', (.1, 700), None, 'plan: its height'),
        'top': ('num', (0, 1), 1.0, 'plan: its top shrunk toward its centre (0: to a point)'),
        'section_m': ('pts', 3, None, '[[across, up], ...] metres: an outline laid along its y instead (a vault, a nave with its aisles)'),
        'length_m': ('num', (.1, 2000), None, 'section: how long'),
    }, 'any solid carried straight: a plan raised (holes allowed) or a section laid along'),
    'parts': ({
        'parts': ('list', None, REQ, 'the landmarks it is made of, each of any kind above (not parts), each with at, theta_deg, z_m and repeat; its basis is the whole\'s'),
    }, 'several classes put together: a domed hall with its portico, a cathedral with towers, a mosque with minarets'),
}
KINDS = tuple(FIELDS)
# a key YAML reads as true or false (PyYAML, YAML 1.1: on, off, yes, no, true, false) can never be written: no field may be one
_YAML_BOOL = {'true', 'false', 'yes', 'no', 'on', 'off'}
def _keys(spec):
    for k, (t, arg, _, _) in spec.items():
        yield k
        if t in ('obj', 'list') and isinstance(arg, dict): yield from _keys(arg)
_bad = _YAML_BOOL & {k.lower() for sp in [COMMON, PART] + [f for f, _ in FIELDS.values()] for k in _keys(sp)}
assert not _bad, f'landmarks: fields named as YAML booleans: {_bad}'


# ------------------------------------------------------------------ checking
def _field(v, spec, where):
    t, arg, _, _ = spec
    def bad(m): raise Bad(f'{where}: {v!r}: {m}')
    isnum = lambda q: isinstance(q, (int, float)) and not isinstance(q, bool)
    if t == 'str':
        if not str(v or '').strip(): bad('a text')
        return str(v)
    if t == 'bool':
        if not isinstance(v, bool): bad('true or false')
        return v
    if t in ('num', 'int'):
        if not isnum(v) or (t == 'int' and float(v) != int(v)): bad('a whole number' if t == 'int' else 'a number')
        if not arg[0] <= v <= arg[1]: bad(f'from {arg[0]:g} to {arg[1]:g}')
        return int(v) if t == 'int' else float(v)
    if t == 'enum':
        if v not in arg: bad(f'one of {", ".join(arg)}')
        return v
    if t == 'pair':
        v_ = [v, v] if isnum(v) else v
        if not (isinstance(v_, list) and len(v_) == 2 and all(isnum(q) and arg[0] <= q <= arg[1] for q in v_)): bad(f'[a, b] (or one number), each from {arg[0]:g} to {arg[1]:g}')
        return [float(q) for q in v_]
    if t == 'll':
        if not (isinstance(v, list) and len(v) == 2 and all(isnum(q) for q in v)): bad('[lon, lat]')
        return [float(q) for q in v]
    if t == 'pts':
        if not (isinstance(v, list) and len(v) >= arg and all(isinstance(q, list) and len(q) == 2 and all(isnum(c) for c in q) for q in v)): bad(f'[[x, y], ...], {arg} points or more')
        return [[float(c) for c in q] for q in v]
    if t == 'rings':
        if not isinstance(v, list): bad('a list of outlines')
        return [_field(r, ('pts', 3, None, ''), f'{where}[{i}]') for i, r in enumerate(v)]
    if t == 'obj':
        if not isinstance(v, dict): bad('a mapping of its keys')
        return _fields(v, arg, where)
    if t == 'list':
        if not isinstance(v, list) or not v: bad('a list')
        return [_field(q, ('obj', arg, None, ''), f'{where}[{i}]') for i, q in enumerate(v)] if arg else v
    raise ValueError(t)


def _fields(D, spec, where):
    extra = sorted(map(str, set(D) - set(spec)))   # (a YAML key on, off, yes or no reads as true or false)
    if extra: raise Bad(f'{where}: no key {", ".join(extra)} (it has {", ".join(spec)})')
    out = {}
    for k, s in spec.items():
        if k in D and D[k] is not None: out[k] = _field(D[k], s, f'{where}.{k}')
        elif s[2] is REQ: raise Bad(f'{where}.{k} is missing: {s[3]}')
        elif s[2] is not None: out[k] = _field(s[2], s, f'{where}.{k}') if s[0] == 'obj' else s[2]
    return out


def check(L, src, part=False):
    """a landmark of one of KINDS checked and completed (FIELDS); src names it in messages. part: a part of `parts` (no lon,
    lat, basis of its own needed; at, repeat allowed). Bad says what to write"""
    if not isinstance(L, dict) or L.get('kind') not in KINDS: raise Bad(f'{src}: kind {L.get("kind") if isinstance(L, dict) else L!r}: one of {", ".join(KINDS)}')
    k = L['kind']; spec_, _ = FIELDS[k]
    com = dict(COMMON)
    if part:
        com.update(PART); com['basis'] = ('str', None, None, COMMON['basis'][3])
        for q in ('lon', 'lat', 'id', 'group'): com.pop(q)   # (a stage selects a whole landmark, not one of its parts)
    out = _fields(L, {**com, **spec_}, src)
    if not part and k != 'arches' and ('lon' not in out or 'lat' not in out): raise Bad(f'{src}: lon and lat are missing: its centre')
    if k == 'arches':
        if ('from' in out) != ('to' in out): raise Bad(f'{src}: from and to go together (a run between two points)')
        if 'from' in out and ('lon' in out or 'length_m' in out): raise Bad(f'{src}: from and to give its place and length: no lon, lat or length_m with them')
        if 'from' not in out and 'length_m' not in out: raise Bad(f'{src}: length_m is missing (or give from and to)')
        if 'from' not in out and not part and 'lon' not in out: raise Bad(f'{src}: lon and lat are missing (or give from and to)')
        tier = out['h_m'] - out['attic_m']
        if tier <= 0: raise Bad(f'{src}: attic_m {out["attic_m"]:g} leaves no room for the arches under h_m {out["h_m"]:g}')
    if k == 'column':
        if 'stages' in out and ('w_m' in out or 'h_m' in out): raise Bad(f'{src}: stages give the widths and heights: no w_m or h_m with them')
        if 'stages' not in out and ('w_m' not in out or 'h_m' not in out): raise Bad(f'{src}: w_m and h_m are missing (or give stages)')
    if k == 'ring':
        o, i = out['outer_m'], out['inner_m']
        if out['plan'] in ('round', 'half'): o, i = [o[0], o[0]], [i[0], i[0]]; out['outer_m'], out['inner_m'] = o, i
        if not (i[0] < o[0] and i[1] < o[1]): raise Bad(f'{src}: inner_m {i} must be inside outer_m {o}')
        if out['plan'] in ('obround', 'u') and o[0] <= o[1]: raise Bad(f'{src}: an {out["plan"]} ring is longer than it is wide (outer_m [length, width])')
        if out['plan'] != 'half' and 'stage' in L: raise Bad(f'{src}: stage: only a half ring (a theatre) has one')
        if out['plan'] not in ('obround', 'u') and 'spina' in L: raise Bad(f'{src}: spina: only an obround or u ring (a circus) has one')
    if k == 'prism':
        if ('plan_m' in out) == ('section_m' in out): raise Bad(f'{src}: give plan_m (with h_m) or section_m (with length_m)')
        if 'plan_m' in out and 'h_m' not in out: raise Bad(f'{src}: h_m is missing: the plan\'s height')
        if 'section_m' in out and 'length_m' not in out: raise Bad(f'{src}: length_m is missing: how long the section is laid')
        if 'section_m' in out and (out['holes_m'] or out['top'] != 1): raise Bad(f'{src}: holes_m and top go with plan_m')
    if k == 'parts':
        out['parts'] = [check(q, f'{src}.parts[{i}]', part=True) for i, q in enumerate(out['parts'])]
        if any(q['kind'] == 'parts' for q in out['parts']): raise Bad(f'{src}: a part is one of the classes, not parts again')
        for i, q in enumerate(out['parts']):
            if q.get('atop') is not None and not q['atop'] < i: raise Bad(f'{src}.parts[{i}].atop: {q["atop"]}: an earlier part (0 to {i - 1})')
    if part and 'repeat' in out and len(out['repeat']) != 1: raise Bad(f'{src}.repeat: one of mirror, ring, line, corners')
    return out


def checked(spec, label='city'):
    """the city's landmarks of KINDS checked and completed in place (others are the generator's own kinds, left as they are);
    stops compile with what to write"""
    for i, L in enumerate(spec.get('landmarks') or []):
        if not isinstance(L, dict) or L.get('kind') not in KINDS + C.BUILTIN_LANDMARKS:   # (an unknown kind drew nothing, without a word)
            raise SystemExit(f'citygen: {label}: landmarks[{i}]: kind {L.get("kind") if isinstance(L, dict) else L!r}: one of the classes for any region ({", ".join(KINDS)}; docs/MODEL.md "Landmarks of any region") or the generator\'s own ({", ".join(C.BUILTIN_LANDMARKS)})')
        if L.get('kind') in KINDS:
            try: spec['landmarks'][i] = check(L, f'{label}: landmarks[{i}]{" (" + L["name"] + ")" if L.get("name") else ""}')
            except Bad as e: raise SystemExit(f'citygen: {e} (docs/MODEL.md "Landmarks of any region"; every key: uv run python -I pipeline/landmarks.py {L.get("kind")})')
    return spec


# ------------------------------------------------------------------ profiles (r a share of the half width, y of the height; from the base round to the axis)
def _arc(n, f): return [f(i / n) for i in range(1, n + 1)]


def profile(shape, rise_share=None):
    """a dome's or a crown's section by name; rise_share (its rise over its width) shapes the saucer and the pointed one"""
    if shape == 'hemisphere': return C.DOME
    if shape == 'onion': return C.ONION
    if shape == 'cone': return [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    if shape == 'bulbous': return [(0.0, 0.0), (.8, 0.0), (.92, .12), (1.0, .3), (.97, .5), (.8, .7), (.5, .86), (.2, .96), (0.0, 1.0)]
    if shape == 'helmet': return [(0.0, 0.0), (1.0, 0.0), (1.0, .25), (.93, .5), (.72, .74), (.4, .9), (.12, .98), (0.0, 1.0)]
    if shape == 'bell': return [(0.0, 0.0), (1.0, 0.0), (.9, .08), (.86, .25), (.76, .45), (.58, .64), (.36, .8), (.14, .93), (0.0, 1.0)]
    if shape == 'shikhara': return [(0.0, 0.0), (1.0, 0.0), (1.0, .12), (.97, .35), (.9, .58), (.76, .78), (.52, .93), (.3, 1.0), (0.0, 1.0)]
    k = 2 * (rise_share if rise_share is not None else {'saucer': .25, 'pointed': .74}[shape])   # rise over the half width
    if shape == 'saucer' or k <= 1:   # a cap of a sphere
        k = min(k, 1.0); rho = (1 + k * k) / (2 * k); p0 = math.asin(min(1.0, 1 / rho))
        return [(0.0, 0.0)] + [(round(rho * math.sin(p0 * (1 - t)), 5), round((rho * math.cos(p0 * (1 - t)) - rho * math.cos(p0)) / k, 5)) for t in [i / 12 for i in range(13)]]
    rho = (k * k + 1) / 2; c = 1 - rho   # pointed: two arcs of radius rho (half widths) centred c off the axis, meeting on it
    return [(0.0, 0.0)] + [(round(1 - t, 5), round(math.sqrt(max(0.0, rho * rho - (1 - t - c) ** 2)) / k, 5)) for t in [i / 12 for i in range(13)]]


RISE = {'hemisphere': .5, 'saucer': .25, 'pointed': .74, 'onion': 1.0, 'bulbous': .9, 'helmet': .7, 'bell': 1.0, 'cone': .8}   # rise over width
NECK = {'onion': .7, 'bulbous': .8}   # a dome wider than its drum: the drum's share of its width


def sides_of(section, sides=None):
    return sides or {'round': 0, 'square': 4, 'octagon': 8, 'hexagon': 6, 'rect': 4}[section]


# ------------------------------------------------------------------ drawing
class Draw:
    """one landmark's drawing: the Builder, the ground its parts stand on (one level plane: a monument is built level, on a
    platform on a slope) and the frame of the piece being drawn"""
    def __init__(self, B, g):
        self.B, self.g = B, g

    def frame(self, x, y, th): return C.Builder.frame(x, y, th)

    def box(self, P, th, lx, ly, z, w, d, h, part=C.LMK): self.B._emit(C.BOX, *P(lx, ly), th, z, w, d, h, part=part, g_m=self.g)

    def frustum(self, P, th, lx, ly, z, w0, d0, h, w1, d1, part=C.LMK): self.B._emit(C.FRUSTUM, *P(lx, ly), th, z, w0, d0, h, w1, d1, part=part, g_m=self.g)

    def turn(self, P, th, lx, ly, z, w, d, h, prof, sides=0, part=C.LMK, sweep=1.0, inset=False, true=False, steps=48):
        """a solid of revolution (sides 0: round in `steps`; a polygon turned so a face looks to the front), h exaggerated unless true"""
        n = sides or steps
        self.B.revolve(*P(lx, ly), th + (math.pi / n if sides else 0), z, w, d, h / (self.B.hex if true else 1), prof, n, part=part, g_m=self.g, sweep=sweep, inset=inset)

    def poly_w(self, w, sides):   # a polygon of `sides` w across its faces -> across its corners (revolve measures to the corners)
        return w / math.cos(math.pi / sides) if sides else w

    def shaft(self, P, th, z, sec, sides, w, d, h, taper, part=C.LMK):
        """an upright body: a frustum on a rectangle, else a polygon or a round turned; its top at z + h"""
        if sec == 'rect' and not sides: self.frustum(P, th, 0, 0, z, w, d, h, w * taper, d * taper, part); return
        n = sides_of(sec, sides); W = self.poly_w(w, n)
        prof = [(0.0, 0.0), (1.0, 0.0), (taper, 1.0), (0.0, 1.0)] if taper > 0 else [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
        self.turn(P, th, 0, 0, z, W, W, h, prof, n, part)

    def cols(self, pts, z, h, dia):
        for x, y in pts: self.B._emit(C.CYL, x, y, 0, z, dia / 2, 0, h, part=C.LMK, g_m=self.g)

    def merlons(self, P, th, z, w, d, h, m, round_=False):
        """battlements round a w x d top at z (round: on its circle)"""
        if self.B.det < 1: return
        if round_:
            n = max(6, int(math.pi * w / (2 * m)))
            for i in range(n):
                a = i / n * math.tau; self.box(P, th + a, w / 2 * math.cos(a) - 0, w / 2 * math.sin(a), z, .6, m, h)
            return
        for side, L_ in ((0, w), (1, d), (2, w), (3, d)):
            n = max(2, int(L_ / (2 * m)))
            for i in range(n):
                t = -L_ / 2 + (i + .5) * L_ / n
                lx, ly = ((t, -d / 2 + .3), (w / 2 - .3, t), (t, d / 2 - .3), (-w / 2 + .3, t))[side]
                self.box(P, th, lx, ly, z, m if side % 2 == 0 else .6, .6 if side % 2 == 0 else m, h)


def roof(D, P, th, z, w, d, R, along_y=True, part=C.LROOF):
    """a roof over a w (across) x d (along) body, its eaves at z; ridge along the frame's y (along_y), else along x"""
    B = D.B
    if not along_y: th, w, d = th + math.pi / 2, d, w
    s, o = R['shape'], R.get('overhang_m') if R.get('overhang_m') is not None else .6
    pitch = R.get('pitch_deg') or {'gabled': 22, 'hipped': 25, 'hip_gable': 28, 'pyramidal': 30, 'mansard': 70, 'flat': 0, 'vault': 0}[s]
    tn = math.tan(math.radians(pitch)); x, y = P(0, 0)
    if R.get('flared'):   # the generator's East Asian roofs (Builder.roof: its long side along its x)
        style = {('gabled', 1): 'gable', ('hipped', 1): 'hip', ('hip_gable', 1): 'xieshan', ('hipped', 2): 'double_hip', ('hip_gable', 2): 'double'}.get((s, R.get('eaves', 1)))
        if style is None: raise SystemExit(f'citygen: a flared roof is gabled, hipped or hip_gable (with eaves 2: hipped or hip_gable), not {s} with eaves {R.get("eaves", 1)}')
        B.roof(x, y, th + math.pi / 2, z, d, w, w / 2 * tn, style, part=part, g=D.g, o=o); return
    for i in range(R.get('eaves', 1) - 1):   # the lower eaves: a skirt, a short wall above it, the next roof smaller
        W, Dd = w + 2 * o, d + 2 * o; rh = min(w, d) * .5 * tn * .3
        B._emit(C.FRUSTUM, x, y, th, z, W, Dd, rh, w * .9, d * .9, part=part, g_m=D.g)
        B._emit(C.BOX, x, y, th, z + rh, w * .82, d * .82, rh * 1.2, part=C.LMK, g_m=D.g)
        z += rh * 2.2; w, d = w * .82, d * .82
    W, Dd = w + 2 * o, d + 2 * o
    if s == 'flat':
        B._emit(C.BOX, x, y, th, z, W, Dd, .5, part=part, g_m=D.g)
    elif s == 'gabled':
        B._emit(C.GABLE, x, y, th, z, w, d + 2 * o * .6, w / 2 * tn, o, part=part, g_m=D.g)
    elif s in ('hipped', 'pyramidal'):
        top = (.02, .02) if s == 'pyramidal' else ((.02, max(Dd - W, .02)) if Dd >= W else (max(W - Dd, .02), .02))
        B._emit(C.FRUSTUM, x, y, th, z, W, Dd, min(W, Dd) / 2 * tn, *top, part=part, g_m=D.g)
    elif s == 'hip_gable':   # hipped to .4 of the rise, gabled above
        rh = W / 2 * tn; k = .4
        B._emit(C.FRUSTUM, x, y, th, z, W, Dd, rh * k, W * (1 - k), Dd - W * k, part=part, g_m=D.g)
        B._emit(C.GABLE, x, y, th, z + rh * k, W * (1 - k), Dd - W * k, rh * (1 - k), 0, part=part, g_m=D.g)
    elif s == 'mansard':   # a steep slope a storey high all round, a low hip above
        h1 = min(4.0, .3 * min(w, d)); a = h1 / tn; Wt, Dt = W - 2 * a, Dd - 2 * a
        B._emit(C.FRUSTUM, x, y, th, z, W, Dd, h1, Wt, Dt, part=part, g_m=D.g)
        B._emit(C.FRUSTUM, x, y, th, z + h1, Wt, Dt, min(Wt, Dt) / 2 * math.tan(math.radians(15)), *((.02, max(Dt - Wt, .02)) if Dt >= Wt else (max(Wt - Dt, .02), .02)), part=part, g_m=D.g)
    elif s == 'vault':   # a barrel along the ridge, true like a dome
        k = R.get('rise', .5); n = 12
        if k <= .5: sec = [(w / 2 * math.cos(i / n * math.pi), w * k * math.sin(i / n * math.pi) / B.hex) for i in range(n + 1)]
        else: sec = [(u * w / 2, v * w * k / B.hex) for u, v in [(r_, y_) for r_, y_ in reversed(profile('pointed', k)) if r_ > 0] + [(0.0, 1.0)] + [(-r_, y_) for r_, y_ in profile('pointed', k) if r_ > 0]]
        B.prism(x, y, th, z, [sec], d, along=True, part=part, g_m=D.g)


def extent(L):
    """(half width, half depth) in its own frame, metres, round its anchor: the frame a sheet or a study gives it (the fabric
    keeps clear of the box of what it covers instead, bounds)"""
    k = L['kind']
    if k == 'ring':
        o = L['outer_m']; hw, hd = o[0] / 2, o[1] / 2
        if L['plan'] == 'half': hd = o[0] / 2 + (L.get('stage') or {}).get('d_m', 0)
        return hw, hd
    if k == 'dome':
        r = max(L['d_m'], (L['dome'].get('d_m') or 0)) / 2 + ((L['peristyle']['gap_m'] + 1) if L.get('peristyle') else 0)
        b = L.get('base') or {}
        return max(r, b.get('w_m', 0) / 2), max(r, (b.get('d_m') or b.get('w_m', 0)) / 2)
    if k == 'long_hall':
        hw, hd = L['w_m'] / 2, L['d_m'] / 2
        if L.get('transept'): hw = max(hw, L['transept']['span_m'] / 2)
        if L.get('apse'): hd += L['apse'].get('r_m') or nave_w(L) / 2
        if L.get('podium'): hw += 1; hd += L['podium']['h_m'] * 1.6 + 1
        if L.get('buttresses'): hw += L['buttresses']['depth_m']
        return hw, hd
    if k == 'column':
        ws = [s_['w_m'] + 2 * (s_.get('eave') or {}).get('overhang_m', 0) + 2 * s_['balcony_m'] for s_ in L['stages']] if L.get('stages') else [L['w_m']]
        p = L.get('pedestal') or {}; w = max(ws + [p.get('w_m', 0)])
        return w / 2, max(w, (L.get('d_m') or 0), p.get('d_m') or 0) / 2
    if k == 'stepped':
        hw, hd = L['w_m'] / 2, (L.get('d_m') or L['w_m']) / 2
        return hw + 1, hd + 1
    if k == 'arches':
        return L['length_m'] / 2, max(L['depth_m'], L['deck_m']) / 2
    if k == 'revolve':
        r = max(p[0] for p in L['profile_m']); return r, r * L['oval']
    if k == 'prism':
        pts = L['plan_m'] if 'plan_m' in L else None
        if pts: return max(abs(p[0]) for p in pts), max(abs(p[1]) for p in pts)
        return max(abs(p[0]) for p in L['section_m']), L['length_m'] / 2
    if k == 'parts':
        hw = hd = 1.0
        for q, (px, py, pth) in placed(L):
            a, b = extent(q); c, s = abs(math.cos(pth)), abs(math.sin(pth))
            hw = max(hw, abs(px) + a * c + b * s); hd = max(hd, abs(py) + a * s + b * c)
        return hw, hd
    raise ValueError(k)


def bounds(L):
    """(x0, y0, x1, y1) in its own frame, metres: what it covers, which need not be centred on its anchor (parts set off to
    one side, a plan drawn off its origin). Its level site is laid there; a box round the anchor (extent) laid a platform
    and kept the houses off the side where it built nothing"""
    k = L['kind']
    if k == 'parts':
        xs, ys = [], []
        for q, (px, py, pth) in placed(L):
            u0, v0, u1, v1 = bounds(q); c, s = math.cos(pth), math.sin(pth)
            for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)): xs.append(px + u * c - v * s); ys.append(py + u * s + v * c)
        return min(xs), min(ys), max(xs), max(ys)
    if k == 'prism' and 'plan_m' in L:
        xs, ys = [q[0] for q in L['plan_m']], [q[1] for q in L['plan_m']]
        return min(xs), min(ys), max(xs), max(ys)
    hw, hd = extent(L); return -hw, -hd, hw, hd


def top(L, hx):
    """about how high it stands on screen, metres (its heights exaggerated by hx, a dome's curve true): the sheet frames it"""
    k = L['kind']; z = (L.get('z_m') or 0) * hx
    if k == 'ring': return z + L['h_m'] * hx
    if k == 'dome':
        dm = L['dome']; dw = dm.get('d_m') or L['d_m'] / NECK.get(dm['shape'], 1.0); rise = dm.get('rise_m') or RISE[dm['shape']] * dw
        return z + ((L.get('base') or {}).get('h_m', 0) + L['drum_h_m'] + (L.get('lantern') or {}).get('h_m', 0) + L['finial_m']) * hx + rise * (1 if dm['keep_curve'] else hx)
    if k == 'long_hall':
        R = L['roof']; pitch = R.get('pitch_deg') or 30
        return z + ((L.get('podium') or {}).get('h_m', 0) + L['h_m'] + L['w_m'] / 2 * math.tan(math.radians(min(pitch, 60))) * (.5 if R['shape'] == 'vault' else 1)) * hx
    if k == 'column':
        hs = sum(s_['h_m'] for s_ in L['stages']) if L.get('stages') else L['h_m']
        w_ = (L['stages'][-1]['w_m'] if L.get('stages') else L['w_m'])
        return z + ((L.get('pedestal') or {}).get('h_m', 0) + hs + (L['top'].get('h_m') or (4 * w_ if L['top']['shape'] == 'spire' else w_))) * hx
    if k in ('stepped', 'arches'): return z + L['h_m'] * hx
    if k == 'revolve': return z + max(p[1] for p in L['profile_m']) * (1 if L['keep_curve'] else hx)
    if k == 'prism': return z + (L['h_m'] if 'plan_m' in L else max(p[1] for p in L['section_m'])) * hx
    if k == 'parts':
        tops = []
        for q in L['parts']: tops.append(z + (tops[q['atop']] - z if q.get('atop') is not None else 0) + top(q, hx))
        return max(tops)
    raise ValueError(k)


def nave_w(L):
    return L['w_m'] - (2 * L['aisles']['n'] * L['aisles']['w_m'] if L.get('aisles') else 0) - (2 * colonnade_depth(L) if (L.get('colonnade') or {}).get('at') == 'around' else 0)


def colonnade_depth(L):
    c = L.get('colonnade') or {}
    if not c: return 0.0
    if c.get('depth_m'): return c['depth_m']
    bay = L['w_m'] / max(1, c['n_front'] - 1)
    return bay * (1.0 if c['at'] == 'around' else 2.0)


def placed(L):
    """the parts of a `parts` landmark with their copies: (part, x, y, turn) in the whole's frame (metres, radians)"""
    out = []
    for q in L['parts']:
        th = math.radians(q.get('theta_deg') or 0); ax, ay = q.get('at') or [0.0, 0.0]; r = q.get('repeat') or {}
        if 'mirror' in r:
            m = r['mirror']; out += [(q, (ax, ay, th))]   # (a class is symmetric about its own y axis: its mirror image is it turned)
            if 'x' in m: out.append((q, (-ax, ay, -th)))
            if 'y' in m: out.append((q, (ax, -ay, math.pi - th)))
            if m == 'xy': out.append((q, (-ax, -ay, math.pi + th)))
        elif 'ring' in r:
            n, R_, a0 = r['ring']['n'], r['ring']['r_m'], math.radians(r['ring']['start_deg'])
            out += [(q, (R_ * math.cos(a0 + i / n * math.tau), R_ * math.sin(a0 + i / n * math.tau), th + a0 + i / n * math.tau - math.pi / 2)) for i in range(n)]
        elif 'line' in r:
            dx, dy = r['line']['step_m']; out += [(q, (ax + i * dx, ay + i * dy, th)) for i in range(r['line']['n'])]
        elif 'corners' in r:
            w, d = r['corners']; out += [(q, (sx * w / 2, sy * d / 2, th)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        else: out.append((q, (ax, ay, th)))
    return out


def draw(D, L, x, y, th, z=0.0):
    """one landmark (a part too) with its centre at UTM x, y, its frame turned th, standing z metres above the ground plane"""
    k = L['kind']; P = D.frame(x, y, th); z = z + (L.get('z_m') or 0.0)
    if k == 'parts':   # (a part on another stands on its top: the other's height on screen, back in the metres the walls are exaggerated from)
        tops = []
        for q in L['parts']: tops.append((tops[q['atop']] if q.get('atop') is not None else 0.0) + top(q, D.B.hex))
        for q, (px, py, pth) in placed(L): draw(D, q, *P(px, py), th + pth, z + (tops[q['atop']] / D.B.hex if q.get('atop') is not None else 0.0))
        return
    {'ring': _ring, 'dome': _dome, 'long_hall': _long_hall, 'column': _column, 'stepped': _stepped, 'arches': _arches, 'revolve': _revolve, 'prism': _prism}[k](D, L, P, th, z)


def _ring(D, L, P, th, z):
    (Lx, Ly), (lx, ly), h = L['outer_m'], L['inner_m'], L['h_m']; plan = L['plan']
    band = (Ly - ly) / 2   # the band's depth (its width's): a band of seats keeps one depth all round
    seats = L['section'] == 'seats'
    roof_h = band / 2 * math.tan(math.radians(28)) if (not seats and L['roof'] == 'pitched') else 0.0
    H = h + roof_h
    def sec(T):   # the section over a band `band` deep, as shares of T (r) and H (y): r 1 the outer wall
        ri = 1 - band / T; rim = min(3.0, band * .08) / T
        if seats:   # tiers of seats (maeniana) falling to the floor, a low wall dropping between one and the next
            aw = min(L['arena_wall_m'], h * .5); k = max(2, min(5, round(band / 12))); r0, y0 = 1 - rim, h; dz = .25 * (h - aw) / k
            pr = [(ri, 0.0), (1.0, 0.0), (1.0, h / H), (r0, h / H)]
            for j in range(1, k + 1):
                rj, yj = r0 + (ri - r0) * j / k, y0 + (aw - y0) * j / k
                pr += [(rj, yj / H)] if j == k else [(rj, (yj + dz) / H), (rj, yj / H)]
            return pr
        if roof_h: return [(ri, 0.0), (1.0, 0.0), (1.0, h / H), ((1 + ri) / 2, 1.0), (ri, h / H)]
        return [(ri, 0.0), (1.0, 0.0), (1.0, 1.0), (ri, 1.0)]
    def stand(cx, cy, side, length):   # a straight run of the band along x, its outer edge on `side` (+1: the frame's +y)
        S = [(side * (r_ - .5) * band, q * H) for r_, q in sec(band)]   # (across: from the band's middle, + toward `side`)
        # laid along the frame's x: the prism's own frame turned back a quarter, its across axis is then the frame's -y
        D.B.prism(*P(cx, cy), th - math.pi / 2, z, [[(-u, v) for u, v in S]], length, along=True, part=C.LMK, g_m=D.g)
    if plan in ('oval', 'round'):
        T = min(Lx, Ly) / 2
        try: D.turn(P, th, 0, 0, z, Lx, Ly, H, sec(T), 0, sweep=1.0, inset=Lx != Ly, steps=72)
        except ValueError as e: raise SystemExit(f'citygen: ring {L.get("name") or ""}: {e}: give a wider inner_m')
        arcades(D, P, th, z, L, Lx, Ly, 1.0)
    elif plan == 'half':
        T = Lx / 2; sw = L['sweep_deg'] / 360
        D.turn(P, th, 0, 0, z, Lx, Lx, H, sec(T), 0, sweep=sw, steps=max(12, int(72 * sw)))
        arcades(D, P, th, z, L, Lx, Lx, sw)
        st = L.get('stage')
        if st: D.box(P, th, 0, -st['d_m'] / 2 - 1, z, Lx * (1.0 if sw <= .5 else .8), st['d_m'], st.get('h_m') or h)
    else:   # obround, u: the straight stands between round ends
        R = Ly / 2; T = R; straight = Lx - Ly if plan == 'obround' else Lx - R
        x0 = -Lx / 2 + (R if plan == 'obround' else 0)   # where the straight part starts
        for side in (-1, 1): stand(x0 + straight / 2, side * (R - band / 2), side, straight)
        ends = [(x0 + straight, -math.pi / 2)] + ([(x0, math.pi / 2)] if plan == 'obround' else [])
        for ex, turn_ in ends:   # a half turn facing out along x
            D.turn(D.frame(*P(ex, 0), th + turn_), th + turn_, 0, 0, z, Ly, Ly, H, sec(T), 0, sweep=.5, steps=36)
        if plan == 'u':   # the starting gates across the straight end
            D.box(P, th, x0 + band * .25, 0, z, band * .5, Ly - 2 * band + 1, h * .45)
        sp = L.get('spina')
        if sp: D.box(P, th, x0 + straight / 2 + (R / 2 if plan == 'u' else 0), 0, z, sp['share'] * straight, sp['w_m'], sp['h_m'])


def arcades(D, P, th, z, L, Lx, Ly, sweep):
    """rows of dark openings on a ring's outer wall (an amphitheatre's arcades)"""
    n_st = L['storeys']
    if not n_st or D.B.det < 1: return
    per = math.pi * (3 * (Lx + Ly) / 2 - math.sqrt((3 * Lx + Ly) * (Lx + 3 * Ly)) / 2) * sweep   # (Ramanujan's perimeter)
    n = L.get('bays') or max(8, int(per / 7)); sh = L['h_m'] / n_st
    a0 = -math.pi / 2 - sweep * math.pi if sweep < 1 else 0.0
    for i in range(n):
        a = a0 + (i + .5) / n * sweep * math.tau; ex, ey = Lx / 2 * math.cos(a), -Ly / 2 * math.sin(a)   # (frame y: the engine's -z)
        nx, ny = Ly / 2 * math.cos(a), -Lx / 2 * math.sin(a); nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
        bw = per / n * .5
        for s in range(n_st):
            D.box(P, th + math.atan2(ny, nx) - math.pi / 2, ex + nx * .05, ey + ny * .05, z + s * sh + sh * .12, bw, .3, sh * .62, part=C.DARK)


def _dome(D, L, P, th, z):
    B = D.B; n = L['sides']; dm = L['dome']; shape = dm['shape']; sw = L['sweep_deg'] / 360
    b = L.get('base')
    if b: D.box(P, th, 0, 0, z, b['w_m'], b.get('d_m') or b['w_m'], b['h_m']); z += b['h_m']
    W = D.poly_w(L['d_m'], n)
    if L['drum_h_m']:
        D.turn(P, th, 0, 0, z, W, W, L['drum_h_m'], [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], n, sweep=sw); z += L['drum_h_m']
    ps = L.get('peristyle')
    if ps:   # columns round the drum, a ring of entablature on them
        R_ = L['d_m'] / 2 + ps['gap_m']; hh = ps.get('h_m') or L['drum_h_m'] or 6.0; z0 = z - (L['drum_h_m'] or 0)
        D.cols([P(R_ * math.cos(i / ps['n'] * math.tau), R_ * math.sin(i / ps['n'] * math.tau)) for i in range(ps['n'])], z0, hh, ps['col_m'])
        D.turn(P, th, 0, 0, z0 + hh, 2 * R_ + ps['col_m'] * 2, 2 * R_ + ps['col_m'] * 2, max(.8, hh * .1), [(L['d_m'] / 2 / (R_ + ps['col_m']), 0.0), (1.0, 0.0), (1.0, 1.0), (L['d_m'] / 2 / (R_ + ps['col_m']), 1.0)], 0)
    dw = dm.get('d_m') or L['d_m'] / NECK.get(shape, 1.0); dwW = D.poly_w(dw, n)
    rise = dm.get('rise_m') or RISE[shape] * dw
    D.turn(P, th, 0, 0, z, dwW, dwW, rise, profile(shape, rise / dw), n, part=C.LROOF, sweep=sw, true=dm['keep_curve'])
    top = z + rise / (B.hex if dm['keep_curve'] else 1)   # metres before the walls' exaggeration (z is too)
    if L['oculus_m'] and sw == 1: D.B._emit(C.CYL, *P(0, 0), 0, top - .03 * rise / (B.hex if dm['keep_curve'] else 1), L['oculus_m'] / 2, 0, .4, part=C.DARK, g_m=D.g)
    ln = L.get('lantern')
    if ln and sw == 1:
        D.turn(P, th, 0, 0, top - .02 * rise, ln['d_m'], ln['d_m'], ln['h_m'] * .7, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], n)
        cap = {'dome': 'hemisphere', 'cone': 'cone', 'onion': 'onion', 'point': 'cone'}[ln['top']]
        D.turn(P, th, 0, 0, top - .02 * rise + ln['h_m'] * .7, ln['d_m'] * (1.2 if cap == 'onion' else 1), ln['d_m'] * (1.2 if cap == 'onion' else 1), ln['h_m'] * .3 * (3 if ln['top'] == 'point' else 1), profile(cap), n, part=C.LROOF)
        top += ln['h_m'] * (1.6 if ln['top'] == 'point' else 1)
    if L['finial_m'] and sw == 1: D.B._emit(C.CYL, *P(0, 0), 0, top - .2, max(.15, L['d_m'] * .006), 0, L['finial_m'], part=C.LMK, g_m=D.g)


def _long_hall(D, L, P, th, z):
    B = D.B; w, d, h = L['w_m'], L['d_m'], L['h_m']
    pod = L.get('podium'); col = L.get('colonnade') or {}; dep = colonnade_depth(L)
    if pod:
        ph = pod['h_m']
        if pod['stair'] == 'around':   # three steps all round (a stylobate)
            for i in range(3): D.box(P, th, 0, 0, z + ph * i / 3, w + 2 * (3 - i) * ph / 3 * 1.4, d + 2 * (3 - i) * ph / 3 * 1.4, ph / 3)
        else:
            D.box(P, th, 0, 0, z, w + 1.0, d + 1.0, ph)
            if pod['stair'] == 'front': B.stair(P, 0, -d / 2 - .5, th, w * .7, ph, ph * 1.6, D.g, z0=z, part=C.LMK)
        z += ph
    # the body: inside a colonnade round it, behind a portico, or the whole; the nave between its aisles
    bx0, bx1, by0, by1 = -w / 2, w / 2, -d / 2, d / 2
    if col.get('at') == 'around': bx0, bx1, by0, by1 = bx0 + dep, bx1 - dep, by0 + dep, by1 - dep
    elif col.get('at') == 'front': by0 += dep
    elif col.get('at') == 'front_back': by0, by1 = by0 + dep, by1 - dep
    bw, bd, cy = bx1 - bx0, by1 - by0, (by0 + by1) / 2
    ai = L.get('aisles'); nw = bw - (2 * ai['n'] * ai['w_m'] if ai else 0)
    if nw < 1: raise SystemExit(f'citygen: long_hall {L.get("name") or ""}: its aisles leave no nave (w_m {w:g})')
    D.box(P, th, 0, cy, z, nw, bd, h)
    if ai:
        for side in (-1, 1):
            aw = ai['n'] * ai['w_m']; ax = side * (nw / 2 + aw / 2)
            D.box(P, th, ax, cy, z, aw, bd, ai['h_m'])
            lx, ly = P(ax, cy)
            B.lean(lx, ly, th + side * math.pi / 2, bd, aw + .6, z + ai['h_m'] + min(3.0, (h - ai['h_m']) * .6), min(3.0, (h - ai['h_m']) * .6), part=C.LROOF, g=D.g)
            if B.det >= 1 and h - ai['h_m'] > 3:   # the clerestory's windows
                k_ = max(2, int(bd / 6))
                for i in range(k_): D.box(P, th, side * (nw / 2 + .05), cy - bd / 2 + (i + .5) * bd / k_, z + ai['h_m'] + (h - ai['h_m']) * .45, .3, bd / k_ * .45, (h - ai['h_m']) * .35, part=C.DARK)
    if col:   # the columns: on the roof's edge line
        n_f = col['n_front']; ch = col.get('h_m') or h; dia = min(2.4, w / max(1, n_f - 1) * .35)
        xs = [-w / 2 + dia / 2 + i * (w - dia) / (n_f - 1) for i in range(n_f)]; sp = (w - dia) / (n_f - 1)
        pts = []
        if col['at'] in ('front', 'front_back', 'around'): pts += [P(x_, -d / 2 + dia / 2) for x_ in xs]
        if col['at'] in ('front_back', 'around'): pts += [P(x_, d / 2 - dia / 2) for x_ in xs]
        if col['at'] == 'around':
            n_s = max(2, round((d - dia) / sp))
            pts += [P(sx * (w / 2 - dia / 2), -d / 2 + dia / 2 + i * (d - dia) / n_s) for sx in (-1, 1) for i in range(1, n_s)]
        elif col['at'] in ('front', 'front_back') and dep > sp * 1.2:   # a deep portico: a column at each side between
            for yy in ([-d / 2 + dep / 2] + ([d / 2 - dep / 2] if col['at'] == 'front_back' else [])): pts += [P(sx * (w / 2 - dia / 2), yy) for sx in (-1, 1)]
        D.cols(pts, z, ch, dia)
        D.box(P, th, 0, 0, z + ch, w, d, max(.8, ch * .12))   # the entablature over the columns and the walls
    # the roof: over the whole when a colonnade carries it, else the nave
    eave = z + (max(h, (col.get('h_m') or h) + max(.8, (col.get('h_m') or h) * .12)) if col else h)
    if col: roof(D, P, th, eave, w, d, L['roof'])
    else: roof(D, D.frame(*P(0, cy), th), th, z + h, nw, bd, L['roof'])
    ap = L.get('apse')
    if ap:   # half round, under a half dome
        r = ap.get('r_m') or nw / 2; ah = ap.get('h_m') or h
        for end in (('back',) if ap['at'] == 'back' else ('front',) if ap['at'] == 'front' else ('back', 'front')):
            sgn = 1 if end == 'back' else -1; Q = D.frame(*P(0, cy + sgn * bd / 2), th + (0 if sgn > 0 else math.pi))
            D.turn(Q, th + (0 if sgn > 0 else math.pi), 0, 0, z, 2 * r, 2 * r, ah, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], 0, sweep=.5)
            D.turn(Q, th + (0 if sgn > 0 else math.pi), 0, 0, z + ah, 2 * r, 2 * r, r, profile('hemisphere'), 0, part=C.LROOF, sweep=.5, true=True)
    tr = L.get('transept')
    if tr:   # an arm across: its own walls and roof, its ridge across
        tw = tr.get('w_m') or nw; th_ = tr.get('h_m') or h; ty = -d / 2 + tr['at'] * d
        D.box(P, th, 0, ty, z, tr['span_m'], tw, th_)
        roof(D, D.frame(*P(0, ty), th), th, z + th_, tr['span_m'], tw, L['roof'], along_y=False)
    bu = L.get('buttresses')
    if bu:
        n_b = bu.get('n') or max(2, int(bd / 7)); out_x = (nw / 2 + (ai['n'] * ai['w_m'] if ai else 0)); bh = (ai['h_m'] if ai else h * .8)
        for side in (-1, 1):
            for i in range(n_b):
                yy = cy - bd / 2 + (i + .5) * bd / n_b
                D.box(P, th, side * (out_x + bu['depth_m'] / 2), yy, z, bu['depth_m'], 1.4, bh + 1.5)
                if bu['flying'] and ai:   # a strut from the pier's head over the aisle to the nave's wall
                    gap = ai['n'] * ai['w_m'] + bu['depth_m'] / 2; h0, h1 = bh + 1.0, h * .82
                    sec = [(0.0, h0), (gap, h1), (gap, h1 + 1.2), (0.0, h0 + 1.6)]
                    sx, sy = P(side * (out_x + bu['depth_m'] / 2), yy)
                    B.prism(sx, sy, th + (math.pi if side > 0 else 0), z, [[(u, v) for u, v in sec]], .9, along=True, part=C.LMK, g_m=D.g)


def _column(D, L, P, th, z):
    B = D.B; sec0 = L['section']; sd0 = L.get('sides')
    p = L.get('pedestal')
    if p: D.box(P, th, 0, 0, z, p['w_m'], p.get('d_m') or p['w_m'], p['h_m']); z += p['h_m']
    stages = L.get('stages') or [{'section': sec0, 'sides': sd0, 'w_m': L['w_m'], 'd_m': L.get('d_m'), 'h_m': L['h_m'], 'taper': L['taper'], 'balcony_m': 0.0}]
    w_top = d_top = sec_t = sides_t = None
    for s_ in stages:
        sec = s_.get('section') or sec0; sd = s_.get('sides') or (sd0 if not s_.get('section') else None); w = s_['w_m']; dd = s_.get('d_m') or w; tp = s_.get('taper', 1.0)
        D.shaft(P, th, z, sec, sd, w, dd, s_['h_m'], tp); z += s_['h_m']
        w_top, d_top, sec_t, sides_t = w * tp, dd * tp, sec, sd
        n = sides_of(sec, sd)
        if s_.get('balcony_m'):   # a ledge round its top
            bw = w * tp + 2 * s_['balcony_m']
            if sec == 'rect' and not sd: D.box(P, th, 0, 0, z - .5, bw, dd * tp + 2 * s_['balcony_m'], .5)
            else: D.turn(P, th, 0, 0, z - .5, D.poly_w(bw, n), D.poly_w(bw, n), .5, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], n)
        ev = s_.get('eave')
        if ev:   # a roof skirt round its top
            o, eh = ev['overhang_m'], ev['h_m']; ww = w * tp
            if sec == 'rect' and not sd or n == 4: D.frustum(P, th, 0, 0, z - eh * .6, ww + 2 * o, (dd * tp if sec == 'rect' else ww) + 2 * o, eh, ww * .96, (dd * tp if sec == 'rect' else ww) * .96, part=C.LROOF)
            else:
                Wo = D.poly_w(ww + 2 * o, n); ri = (ww / 2) / ((ww + 2 * o) / 2)
                D.turn(P, th, 0, 0, z - eh * .6, Wo, Wo, eh, [(ri * .9, 0.0), (1.0, 0.0), (ri * .96, 1.0), (ri * .9, 1.0)], n, part=C.LROOF)
    pa = L.get('parapet')
    if pa: D.merlons(P, th, z, w_top, d_top, pa['h_m'], pa['merlon_m'], round_=sec_t == 'round' and not sides_t)
    t = L['top']; s = t['shape']
    if s == 'flat': return
    tw = t.get('w_m') or w_top; n = sides_of(sec_t, sides_t)
    hd = {'pyramid': .7, 'cone': 1.0, 'spire': 4.0, 'dome': .5, 'onion': 1.0, 'bulbous': .9, 'helmet': .7, 'statue': 1.2, 'lantern': 1.2, 'shikhara': 1.6}[s]
    th_ = t.get('h_m') or hd * tw
    if s in ('pyramid', 'spire', 'cone'):
        if sec_t == 'rect' and not sides_t and s != 'cone': D.frustum(P, th, 0, 0, z, tw, (t.get('w_m') or d_top), th_, .02, .02, part=C.LROOF)
        else: D.turn(P, th, 0, 0, z, D.poly_w(tw, 0 if s == 'cone' else n), D.poly_w(tw, 0 if s == 'cone' else n), th_, profile('cone'), 0 if s == 'cone' else n, part=C.LROOF)
    elif s in ('dome', 'onion', 'bulbous', 'helmet'):
        shp = 'hemisphere' if s == 'dome' else s; ww = tw / NECK.get(shp, 1.0)
        D.turn(P, th, 0, 0, z, D.poly_w(ww, n), D.poly_w(ww, n), t.get('h_m') or RISE[shp] * ww, profile(shp), n, part=C.LROOF, true=True)
    elif s == 'shikhara':
        D.turn(P, th, 0, 0, z, D.poly_w(tw, 4), D.poly_w(tw, 4), th_, profile('shikhara'), 4, part=C.LROOF)
        D.turn(P, th, 0, 0, z + th_ - .1, tw * .45, tw * .45, tw * .12, [(0.0, 0.0), (.8, 0.0), (1.0, .5), (.8, 1.0), (0.0, 1.0)], 0, part=C.LROOF)   # the amalaka
    elif s == 'statue':
        D.box(P, th, 0, 0, z, tw * .35, tw * .35, th_)
    elif s == 'lantern':
        D.turn(P, th, 0, 0, z, tw * .6, tw * .6, th_ * .6, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], 0)
        D.turn(P, th, 0, 0, z + th_ * .6, tw * .6, tw * .6, tw * .3, profile('hemisphere'), 0, part=C.LROOF, true=True)


def _stepped(D, L, P, th, z):
    w = L['w_m']; d = L.get('d_m') or w; h, n, top = L['h_m'], L['tiers'], L['top']; plan = L['plan']
    ws = [1 - (1 - top) * i / n for i in range(n + 1)]   # each tier's foot, as a share of the foot; ws[n] the top
    if plan in ('round', 'polygon'):   # one turned section stepping in
        sides = 0 if plan == 'round' else L['sides']; prof = [(0.0, 0.0), (1.0, 0.0)]
        if n == 1 and L['slope'] == 'battered': prof.append((top, 1.0))
        else:
            for i in range(n):
                y1 = (i + 1) / n
                prof += [(ws[i], y1), (ws[i + 1], y1)] if L['slope'] == 'vertical' else [((ws[i] + ws[i + 1]) / 2, y1), (ws[i + 1], y1)]
        if prof[-1][0] > 0: prof.append((0.0, 1.0))
        prof = [prof[0]] + [q for a_, q in zip(prof, prof[1:]) if q != a_]
        W = D.poly_w(w, sides); D.turn(P, th, 0, 0, z, W, W, h, prof, sides)
    else:
        for i in range(n):
            a, b = ws[i], ws[i + 1]
            if L['slope'] == 'vertical': D.box(P, th, 0, 0, z + h * i / n, w * a, d - w * (1 - a), h / n)
            else:
                t_ = b if n == 1 else (a + b) / 2   # a tier's face leans in half the step, a ledge takes the rest
                D.frustum(P, th, 0, 0, z + h * i / n, w * a, d - w * (1 - a), h / n, max(.02, w * t_), max(.02, d - w * (1 - t_)))
    st = L['stair']
    if st['at'] != 'none':
        sw = st.get('w_m') or w * .15
        # the flight runs from the top platform's edge down past every tier's outer corner (a straight line from the top edge to
        # the foot passes inside the corners of the tiers, which then cut the stair into dashes)
        step_in = w * (1 - top) / 2   # how far the top's edge stands in from the foot
        corners = [((w * ws[i] - w * top) / 2 if L['slope'] == 'vertical' or n == 1 else (w * (ws[i] + ws[i + 1]) / 2 - w * top) / 2, h * (i + 1) / n) for i in range(n)]
        run = max([step_in] + [cx_ / (1 - cy_ / h) for cx_, cy_ in corners if cy_ < h - 1e-6]) + .5
        sides_ = [0] if st['at'] == 'front' else [0, 1, 2, 3]
        for k in sides_:
            ang = th + k * math.pi / 2; dd = d if k % 2 == 0 else w   # (the tiers step in by the same metres on every side)
            Q = D.frame(*P(0, 0), ang)
            if L['slope'] == 'vertical' and n > 1:   # terraces: a short flight up each one's wall from the ledge below it
                for i in range(n):
                    face = (dd / 2 - w * (1 - ws[i]) / 2) if plan == 'rect' else w * ws[i] / 2
                    ledge = w * (ws[i - 1] - ws[i]) / 2 if i else min(h / n * 1.6, w * .1)
                    D.B.stair(Q, 0, -face, ang, sw, h / n, max(.6, ledge * .9), D.g, z0=z + h * i / n, part=C.LMK)
            else:
                face = dd / 2 - step_in if plan == 'rect' else w * top / 2
                D.B.stair(Q, 0, -face, ang, sw, h, run, D.g, z0=z, part=C.LMK)


def _arch_head(u0, u1, vs, kind):
    """an opening's head from its right jamb's top (u1, vs) over to its left one's (u0, vs) (metres, elevation: u along, v up)"""
    r = (u1 - u0) / 2; c = (u0 + u1) / 2; n = 12
    if kind == 'flat': return [(u1, vs), (u0, vs)]
    if kind == 'round': return [(c + r * math.cos(i / n * math.pi), vs + r * math.sin(i / n * math.pi)) for i in range(n + 1)]
    if kind == 'horseshoe':   # a circle wider than the opening, its centre above the jambs' tops: it closes in again below its widest
        R_ = r * 1.15; b = math.acos(r / R_); vc = vs + R_ * math.sin(b)
        return [(c + R_ * math.cos(-b + i / n * (math.pi + 2 * b)), vc + R_ * math.sin(-b + i / n * (math.pi + 2 * b))) for i in range(n + 1)]
    R_ = 1.6 * r; a1 = math.acos((R_ - r) / R_); m = n // 2   # pointed: two arcs of 1.6 times the half span, each centred across the axis
    right = [(u1 - R_ + R_ * math.cos(a1 * i / m), vs + R_ * math.sin(a1 * i / m)) for i in range(m + 1)]
    left = [(u0 + R_ - R_ * math.cos(a1 * (m - i) / m), vs + R_ * math.sin(a1 * (m - i) / m)) for i in range(m + 1)]
    return right + left[1:]


def arch_rise(kind, span):
    r = span / 2
    return {'flat': 0.0, 'round': r, 'horseshoe': r * 1.15 * (1 + math.sin(math.acos(1 / 1.15))), 'pointed': math.sqrt((1.6 * r) ** 2 - (.6 * r) ** 2)}[kind]


def _arches(D, L, P, th, z):
    B = D.B; Lm, h, dep = L['length_m'], L['h_m'], L['depth_m']; nt = L['tiers']; tier = (h - L['attic_m']) / nt
    n = L.get('bays') or max(1, round(Lm / max(1.0, tier * .9)))
    bay = Lm / n; span = bay * L['opening']; rise = arch_rise(L['arch'], span); vs_ = tier * L['spring']
    if vs_ + rise > tier * .94:   # the head must close under the tier's top
        vs_ = max(tier * .15, tier * .94 - rise)
        if vs_ + rise > tier * .94: span = (tier * .94 - vs_) / (rise / span); rise = arch_rise(L['arch'], span)
    outline = [(-Lm / 2, 0.0)]; holes = []   # the elevation (u along, v up), laid through the wall's thickness
    for t in range(nt):
        v0 = t * tier
        for i in range(n):
            c = -Lm / 2 + (i + .5) * bay; head = _arch_head(c - span / 2, c + span / 2, v0 + vs_, L['arch'])
            if t == 0: outline += [(c - span / 2, 0.0)] + head[::-1] + [(c + span / 2, 0.0)]   # (on the ground: a notch in the outline)
            else: holes.append([(c - span / 2, v0), (c + span / 2, v0)] + head)
    outline += [(Lm / 2, 0.0), (Lm / 2, h), (-Lm / 2, h)]
    clean = [outline[0]] + [q for a_, q in zip(outline, outline[1:]) if math.hypot(q[0] - a_[0], q[1] - a_[1]) > 1e-6]
    if math.hypot(clean[-1][0] - clean[0][0], clean[-1][1] - clean[0][1]) < 1e-6: clean.pop()
    if L['through']:
        B.prism(*P(0, 0), th, z, [clean] + holes, dep, along=True, part=C.LMK, g_m=D.g)
    else:
        rc = L.get('recess_m') or dep / 2
        B.prism(*P(0, -dep / 2 + rc / 2), th, z, [clean] + holes, rc, along=True, part=C.LMK, g_m=D.g)
        D.box(P, th, 0, rc / 2, z, Lm, dep - rc, h)   # the solid behind
        for t in range(nt):
            for i in range(n):   # the back of each recess, dark
                c = -Lm / 2 + (i + .5) * bay; D.box(P, th, c, -dep / 2 + rc + .05, z + t * tier, span * .98, .2, vs_ + rise * .9, part=C.DARK)
    if L['deck_m']: D.box(P, th, 0, 0, z + h, Lm, L['deck_m'], .8)


def _revolve(D, L, P, th, z):
    pr = L['profile_m']; R = max(p[0] for p in pr); H = max(p[1] for p in pr)
    if R <= 0 or H <= 0: raise SystemExit(f'citygen: revolve {L.get("name") or ""}: its profile has no width or no height')
    try: D.B.revolve(*P(0, 0), th, z, 2 * R, 2 * R * L['oval'], H / (D.B.hex if L['keep_curve'] else 1), [(p[0] / R, p[1] / H) for p in pr], L['sides'], part=C.LMK, g_m=D.g, sweep=L['sweep_deg'] / 360, inset=L['inset'])
    except ValueError as e: raise SystemExit(f'citygen: revolve {L.get("name") or ""}: {e}')


def _prism(D, L, P, th, z):
    if 'plan_m' in L: D.B.prism(*P(0, 0), th, z, [L['plan_m']] + L['holes_m'], L['h_m'], top=L['top'], part=C.LMK, g_m=D.g)
    else: D.B.prism(*P(0, 0), th, z, [L['section_m']], L['length_m'], along=True, part=C.LMK, g_m=D.g)


FADE_M = 25.0   # metres: the height at which a landmark's exaggeration has faded half way (exaggeration)


def exaggeration(L, city_hex):
    """a landmark's height exaggeration: its own when it gives one; else the city's, fading as the landmark gets taller,
    1 + (x - 1) / (1 + (H / 25 m)^2) with H its true height. A small building is stretched to read at the film's scale as the
    houses are (a 6 m shrine nearly twice), a tall one less (a 48 m amphitheatre 1.2 times), and a monument big enough to read on
    its own keeps the proportions people know it by (stretched twice, a pyramid's 52 degree faces stood at 68). One factor for
    the whole landmark: its shape is scaled, never bent"""
    if L.get('exaggeration'): return float(L['exaggeration'])
    return 1 + (city_hex - 1) / (1 + (top(L, 1.0) / FADE_M) ** 2)


def build(B, L, x, y, th):
    """draw a checked landmark at UTM x, y turned th on one level plane (a platform on a slope); returns its footprint's
    half sizes (metres, its frame) for the fabric to keep clear"""
    hw, hd = extent(L); hx0 = B.hex; B.hex = exaggeration(L, hx0)
    x0, y0, x1, y1 = bounds(L); w, d = x1 - x0, y1 - y0; sx, sy = B.frame(x, y, th)((x0 + x1) / 2, (y0 + y1) / 2)   # (its site: where it stands, not round its anchor)
    try:
        if L['kind'] == 'arches' and L['length_m'] > 120: _run(B, L, x, y, th, hd)
        else:
            # level: a monument is built level, on a platform where the ground falls away under it by more than 2 % of its width
            # (less: its own walls reach down, as the foundation every body has; a square plate under a round building on a gentle
            # slope read wrong)
            s0, p0 = B.lot_slope, B.plinth; B.lot_slope = 0.0; B.plinth = max(B.plinth, .02 * min(w, d))
            try:
                with B.lot_site(sx, sy, th, w, d):
                    g = B.gsite(sx, sy, th, w, d)
                    draw(Draw(B, g), L, x, y, th)
            finally: B.lot_slope, B.plinth = s0, p0
    finally: B.hex = hx0; B.found = 0.0
    return hw, hd


def _run(B, L, x, y, th, hd):
    """a long run of arches (an aqueduct, a bridge): its top straight from one end to the other, h_m above the ground at each
    end, laid in pieces of 80 m or less whose arches reach down to the ground under them (a valley's arches are the taller).
    Pieces each standing h_m above their own ground stepped up and down with it, a saw along the top"""
    Lm = L['length_m']; n = math.ceil(Lm / 80); seg = Lm / n; P = C.Builder.frame(x, y, th)
    tot = L.get('bays') or max(1, round(Lm / max(1.0, (L['h_m'] - L['attic_m']) / L['tiers'] * .9)))
    ga, gb = B.ground_m(*P(-Lm / 2, 0)), B.ground_m(*P(Lm / 2, 0)); gr = (gb - ga) / Lm   # the line's ground, metres per metre along
    s0 = B.slope; B.slope = (gr * math.cos(th), gr * math.sin(th))   # (every piece sheared along it: one straight top)
    try:
        for i in range(n):
            c = -Lm / 2 + (i + .5) * seg; gl = ga + gr * (c + Lm / 2); sx, sy = P(c, 0)
            under = [gl + gr * (u - c) - B.ground_m(*P(u, v)) for u in [c - seg / 2 + seg * k / 6 for k in range(7)] for v in (-hd, 0.0, hd)]
            B.found = max(0.0, max(under))   # (its foundation: down to the lowest ground under it)
            draw(Draw(B, gl), {**L, 'length_m': seg, 'bays': max(1, round(tot / n))}, sx, sy, th)
    finally: B.slope = s0


def describe(kinds=KINDS):
    """every kind's keys as text (the table FIELDS)"""
    out = []
    def keys(spec, ind):
        for k, (t, arg, dflt, help_) in spec.items():
            rng = f' {arg[0]:g}..{arg[1]:g}' if t in ('num', 'int', 'pair') and arg else (f' {"|".join(arg)}' if t == 'enum' else '')
            dv = ' (required)' if dflt is REQ else (f' = {dflt}' if dflt not in (None, {}, []) else '')
            out.append(f'{ind}{k}: {t}{rng}{dv}  {help_}')
            if t in ('obj', 'list') and isinstance(arg, dict): keys(arg, ind + '    ')
    out.append('every landmark of these kinds:'); keys(COMMON, '  ')
    out.append('a part of parts also:'); keys(PART, '  ')
    for k in kinds:
        spec, what = FIELDS[k]; out.append(f'\n{k}: {what}'); keys(spec, '  ')
    return '\n'.join(out)


if __name__ == '__main__':
    ks = sys.argv[1:] or KINDS
    bad = [k for k in ks if k not in KINDS]
    if bad: raise SystemExit(f'landmarks: no kind {", ".join(bad)} (kinds: {", ".join(KINDS)})')
    print(describe(ks))
