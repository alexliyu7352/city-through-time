"""Procedural period cities: a whole city per era, built from a spec (walls, gates, streets, lanes, lot fabric, landmark
compounds, water) into a flat list of primitives the engine merges into one mesh. Every era city is a schematic
reconstruction: its outline follows the sources named in the spec (FACTS.md), the fabric follows the typology of the time.

The detail is sized for the street-level glides (camera ~300-600 m away, about 0.1 m per pixel): roofs have eaves with
thickness, a concave two-step slope, a ridge and ridge-end ornaments; halls stand on podiums with colonnades and dark door
panels; walls carry merlons, bastions (马面), corner towers, gate towers over dark passages, barbicans and a moat; courtyard
houses have their own walls, a gate house, paving and sometimes a tree; streets and lanes are paved strips.

Coordinates: specs are WGS84 lon/lat and metres; the generator works in the city's UTM metres (Frame) and emits model units.
Primitive record (list): [type, cx, cz, rot, y0, a, b, c, d, e, rank, part, g, gx, gz, bx, bz]
  type 0 BOX      a=w (local x), b=d (local z), c=h
  type 1 GABLE    a=span (local x), b=length (local z, ridge direction), c=ridge height, d=overhang
  type 2 FRUSTUM  a=w0, b=d0, c=h, d=w1, e=d1         (stepped terraces; hip roofs when d1 is ~0)
  type 3 CYL      a=r, c=h
  type 4 CONE     a=r, c=h
  rot  radians about +y in model space (model z points south); local x = the UTM direction `theta`
  y0   model height of the primitive's base, g = model ground height under it (the rise pivot)
  rank 0..1, order of appearance (distance from the era's origin, with noise)
  part see the constants below; the engine shades each part (roof tiles darker, openings near black, water glossy)
  gx, gz a shear (model y per model x / z) for pieces laid along a slope; bx, bz the centre of the building the primitive
       belongs to (it rises and falls with it)
Heights: ground relief is exaggerated like the terrain plate (gex); building heights by the era's own factor (hex), so
courtyards keep their proportions while the plateau still reads.
"""
import math, os, random
import numpy as np
from contextlib import contextmanager
import shapely
from shapely.geometry import Polygon, LineString, Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import affinity

BOX, GABLE, FRUSTUM, CYL, CONE = 0, 1, 2, 3, 4
FAB, LMK, WALL, BRIDGE, TREE, WATER, DARK, PAVE, ROOF, LROOF, EARTH = range(11)
PLINTH = 11   # a body's base on a slope (_emit): darker than the walls, so a tall foundation reads as a platform
DETAIL = {'low': 0, 'medium': 1, 'high': 2}


class Builder:
    def __init__(self, F, ground_m, gex, hex_, origin_xy, seed=1, detail='medium'):
        """F: geo.Frame; ground_m(x, y) -> metres of relief (unexaggerated) at a UTM point; gex: ground exaggeration (the
        plate's); hex_: building height exaggeration; detail: low | medium | high"""
        self.F, self.ground_m, self.gex, self.hex = F, ground_m, gex, hex_
        self.ox, self.oy = origin_xy
        self.prims = []
        self.rng = random.Random(seed)
        self.det = DETAIL.get(detail, 1)
        self.skirt = 3.0   # metres of foundation below grade, so nothing floats where the plate and the DEM sample differ (2.5 left four Qin pieces on the 北阪 edge 0.2 m short once the plate lost its fine bumps)
        self.found = 0.0   # metres of relief under the current building (gsite): its foundation reaches that much deeper
        self.clear = .15   # metres a piece laid along the ground (lay) keeps above it: the thin paving never meets the plate
        self.step = .5     # metres of fall along a long wing before it steps down the slope in pieces (gable_house)
        self.plinth = .3   # metres of foundation (self.found) above which a house's or a hall's body gets a plinth (_emit)
        self.slope = None  # (dg/dx, dg/dy) ground metres per metre: the primitives emitted now are laid along a slope (see lay)
        self.site = None   # the lot being built on, made one plane (lot_site): (x, y, height there, slope, foundation)
        self.lot_slope = .04   # the steepest a lot's plane leans (ground metres per metre, before the plate's exaggeration): a house tilts with a gentle slope; on a steeper one it stands on a terrace (a whole house sheared along a hillside reads as falling over, and its roof slopes cross)
        self.gid, self.tag, self.meta = 0, ('misc', 0), []   # building groups (a building rises whole) and what each came from (stages)
        self.types = {}    # the declared house types a fabric can name (house_types), name -> complete type

    # ------------------------------------------------------------------ low level
    def _emit(self, t, x, y, theta, z0, a, b, c, d=0.0, e=0.0, part=FAB, g_m=None, rank=None):
        """x, y UTM metres; theta radians CCW from east (UTM frame); z0 metres above ground; a..e metres. A house's or a hall's
        body on a slope (its foundation deeper than self.plinth) first gets a plinth (PLINTH): a darker base 0.4 m wider all round
        from the foundation's foot up to the ground at its highest corner, so the foundation reads as a platform (台基, 吊腳)
        and not as its walls run down the hill (in the walls' colour it stretches the house)"""
        S = self.F.scale
        gm = self.ground_m(x, y) if g_m is None else g_m
        if t == BOX and z0 <= 1e-6 and part in (FAB, LMK) and d != 1 and not self.slope and self.found > self.plinth and min(a, b) >= 2:
            self._emit(BOX, x, y, theta, 0, a + .8, b + .8, .05, part=PLINTH, g_m=gm, rank=rank)
        mx, mz = self.F.model(x, y)
        r = rank if rank is not None else math.hypot(x - self.ox, y - self.oy)
        base = gm * S * self.gex
        y0 = base + z0 * S * self.hex
        ch = c * S * self.hex
        if z0 <= 1e-6 and t in (BOX, FRUSTUM, CYL):   # a foundation below grade (deeper by the slope under a building on a hillside)
            sk = (self.skirt + self.found) * S * self.gex; y0 -= sk; ch += sk
        pl = lambda v: v * S
        if t == BOX: rec = [t, mx, mz, -theta, y0, pl(a), pl(b), ch, d, 0]   # d: 1 marks a road piece (strip)
        elif t == GABLE: rec = [t, mx, mz, -theta, y0, pl(a), pl(b), ch, pl(d), 0]
        elif t == FRUSTUM: rec = [t, mx, mz, -theta, y0, pl(a), pl(b), ch, pl(d), pl(e)]
        else: rec = [t, mx, mz, 0, y0, pl(a), 0, ch, 0, 0]
        rec = [round(v, 7) if isinstance(v, float) else v for v in rec]
        rec += [r, part, round(base, 7)]
        if self.slope:   # a shear in model space: y += gx * dX + gz * dZ (model z points south, UTM y north)
            rec += [round(self.slope[0] * self.gex, 6), round(-self.slope[1] * self.gex, 6)]
        else: rec += [0, 0]
        self.prims.append(rec); self.meta.append((self.gid, self.tag))

    def group(self, tag=None):
        """start a new building group: its primitives rise and fall together (one house, one hall, one wall piece)"""
        self.gid += 1
        if tag is not None: self.tag = tag

    def finish(self, noise=.08, meta=None):
        """rank = distance of the building's centre from the origin, normalised, with noise per building (not per primitive:
        a roof never rises before its walls). Each record gets its building's centre (model xz) as fields 15, 16; `meta`, when
        a list, receives (group id, source tag, distance in metres) per primitive for compile's stages"""
        if not self.prims: return []
        acc = {}
        for p, (gid, _) in zip(self.prims, self.meta):
            a = acc.setdefault(gid, [0.0, 0.0, 0.0, 0]); a[0] += p[1]; a[1] += p[2]; a[2] += p[10]; a[3] += 1
        ctr = {g: (a[0] / a[3], a[1] / a[3], a[2] / a[3]) for g, a in acc.items()}
        mx = max(c[2] for c in ctr.values()) or 1
        hrand = lambda g: random.Random(g * 7919 + 13).random()
        out = []
        for p, (gid, tag) in zip(self.prims, self.meta):
            cx, cz, dm = ctr[gid]
            r = min(1, max(0, dm / mx * (1 - noise) + hrand(gid) * noise))
            out.append(p[:10] + [round(r, 4)] + p[11:] + [round(cx, 6), round(cz, 6)])
            if meta is not None: meta.append((gid, tag, dm))
        return out

    def gsite(self, x, y, th, w, d):
        """a level site for a w x d footprint on a slope: the building stands at the HIGHEST ground under it (centre, corners,
        edge middles), so the hill never cuts through it, and its foundation reaches down over the slope (self.found), a
        platform showing on the downhill side as on a real hillside"""
        if self.site is not None:   # on a lot made one plane (lot_site): that plane, under every part of the house alike
            x0, y0, g0, sl, fd = self.site; self.found = fd; return g0 + sl[0] * (x - x0) + sl[1] * (y - y0)
        P = self.frame(x, y, th); n = max(3, min(33, int(math.ceil(max(w, d) / 8)) + 1))   # every 8 m or so: finer than the plate's mesh (48 m), so nothing between samples rises through it
        gs = [self.ground_m(*P(w * (i / (n - 1) - .5), d * (j / (n - 1) - .5))) for i in range(n) for j in range(n)]
        self.found = max(gs) - min(gs)
        return max(gs)

    @contextmanager
    def lot_site(self, x, y, th, w, d):
        """a house's lot made one plane before it is built on (平整土地): the plane fitted to the ground under the w x d lot,
        raised just enough that the ground nowhere pokes through it, level where the ground is level and tilted with the hill
        where it is not (up to lot_slope; steeper, the house stands on a terrace whose foundation takes the rest). Where the plane
        stands above the ground by more than self.plinth, the lot is one platform under it (台基, a plinth) down to the ground,
        and the house's walls keep their height on top of it; without it the foundation went into every wall, and a court on a
        steep slope stood behind a wall as tall as a city's. Every part of the house (its wings, walls, gate, court) then stands on that plane (gsite, strip and
        gable_house take it, the pieces are sheared along it), so a house is one piece on the slope: its wings no longer stand
        each on its own level against the walls and the court, nor on plinths of their own. Inside a lot already made one plane
        (a mansion's courts) the plane is the mansion's."""
        if self.site is not None: yield; return
        P = self.frame(x, y, th); n = max(3, min(12, int(math.ceil(max(w, d) / 6)) + 1)); pts = []
        for i in range(n):
            for j in range(n):
                qx, qy = P(w * (i / (n - 1) - .5), d * (j / (n - 1) - .5)); pts.append((qx - x, qy - y, self.ground_m(qx, qy)))
        A = np.array([[1.0, a, b] for a, b, _ in pts]); z = np.array([g for _, _, g in pts])
        c0, bx, by = np.linalg.lstsq(A, z, rcond=None)[0]
        k = min(1.0, self.lot_slope / max(math.hypot(bx, by), 1e-9)); bx, by = bx * k, by * k   # steeper than lot_slope: a terrace, its foundation taking the rest
        res = z - A @ np.array([0.0, bx, by]); c0 = 0.0; lift = float(res.max()) + self.clear
        s0, f0 = self.slope, self.found
        g0, sl, fd = float(c0) + lift, (float(bx), float(by)), lift - float(res.min())
        self.slope = sl
        if fd > self.plinth:   # the platform: a thin top on the plane, its foundation down to the lowest ground under the lot
            self.group(); self.found = fd; self._emit(BOX, x, y, th, 0, w, d, .05, part=PLINTH, g_m=g0); fd = 0.0
        self.site = (x, y, g0, sl, fd); self.found = fd
        try: yield
        finally: self.site = None; self.slope, self.found = s0, f0

    @staticmethod
    def frame(x, y, th):
        """local (lx, ly) -> UTM, local x along th, local y to its left"""
        c, s = math.cos(th), math.sin(th)
        return lambda lx, ly: (x + lx * c - ly * s, y + lx * s + ly * c)

    def lay(self, a, b, w):
        """lay a straight piece a -> b (UTM) of width w along the ground: a plane through the ground at both ends, raised just
        enough that the ground nowhere pokes through. Returns (ground at the centre, slope (dg/dx, dg/dy), foundation depth):
        with self.slope set to that slope, a long wall, corridor or street follows the hill smoothly instead of in level steps"""
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1e-9; ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx, ny = -uy, ux
        ga, gb = self.ground_m(*a), self.ground_m(*b); s = (gb - ga) / L; mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        res = []   # the ground every 4 m along and a quarter of the width across (the plate's mesh creases between its corners)
        nk = max(4, int(math.ceil(L / 4)))
        for k in range(nk + 1):
            for o in (-w / 2, -w / 4, 0.0, w / 4, w / 2):
                qx, qy = a[0] + (b[0] - a[0]) * k / nk + nx * o, a[1] + (b[1] - a[1]) * k / nk + ny * o
                res.append(self.ground_m(qx, qy) - ((ga + gb) / 2 + s * ((qx - mx) * ux + (qy - my) * uy)))
        lift = max(0.0, max(res)) + self.clear
        return (ga + gb) / 2 + lift, (s * ux, s * uy), lift - min(res)

    def strip(self, a, b, w, h=.12, part=PAVE, z0=0.0, piece=30.0, g=None, road=None):
        """a straight strip from a to b (paving, a wall, a moat) laid along the ground (lay), in pieces of at most `piece`
        metres where the slope changes; g: a level strip at that ground instead (on top of a terrace or a platform).
        Neighbouring pieces meet at one height (the higher of the two they were laid at), end to end: the surface runs on
        without steps or overlaps (a step casts a hairline shadow and two overlapping tops flicker: a road looked dashed).
        A paved strip is marked a road (field 8): the engine draws its ruts along it; road=False for a paved court."""
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < .5: return
        th = math.atan2(b[1] - a[1], b[0] - a[0]); road = (1.0 if part == PAVE else 0.0) if road is None else float(road)
        if g is None and self.site is not None: g = self.gsite((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, th, L, w)   # on a lot made one plane: along it (sheared)
        if g is not None: self._emit(BOX, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, th, z0, L, w, h, road, part=part, g_m=g); return
        g3 = (self.ground_m(*a), self.ground_m(*b), self.ground_m((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
        n = max(1, math.ceil(L / piece)) if max(g3) - min(g3) > .25 else 1
        f0 = self.found; ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; Ln = L / n
        P = [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]
        laid = [self.lay(P[i], P[i + 1], w) for i in range(n)]   # (centre height, slope, foundation) per piece
        ends = [(gc - (s[0] * ux + s[1] * uy) * Ln / 2, gc + (s[0] * ux + s[1] * uy) * Ln / 2) for gc, s, _ in laid]
        J = [ends[0][0]] + [max(ends[i - 1][1], ends[i][0]) for i in range(1, n)] + [ends[-1][1]]   # one height per joint
        for i in range(n):
            p, q = P[i], P[i + 1]; sl = (J[i + 1] - J[i]) / Ln
            self.slope = (sl * ux, sl * uy); self.found = laid[i][2] + max(J[i] - ends[i][0], J[i + 1] - ends[i][1])
            self._emit(BOX, (p[0] + q[0]) / 2, (p[1] + q[1]) / 2, th, z0, Ln, w, h, road, part=part, g_m=(J[i] + J[i + 1]) / 2)
        self.slope = None; self.found = f0

    # ------------------------------------------------------------------ roofs
    def roof(self, x, y, th, z0, w, d, rh, style='xieshan', part=LROOF, g=None, o=None, ornaments=None):
        """a roof over a w (local x, the long side) x d body whose eave line is at z0; rh: eave line to ridge.
        styles: gable (悬山), hip (庑殿), xieshan (歇山), double (重檐歇山), double_hip (重檐庑殿), flat"""
        if o is None: o = min(1.8, .1 * d + .4)
        W, D = w + 2 * o, d + 2 * o
        P = self.frame(x, y, th)
        orn = self.det >= 1 if ornaments is None else ornaments
        if style == 'flat':
            self._emit(BOX, x, y, th, z0, W, D, .6, part=part, g_m=g); return
        if style == 'gable':
            self._emit(GABLE, x, y, th + math.pi / 2, z0, d, w + 2 * o * .6, rh, o, part=part, g_m=g)
            self._emit(BOX, x, y, th, z0 + rh - .25, w + 2 * o * .6 + .3, .45, .6, part=part, g_m=g)          # ridge
            return
        if style in ('double', 'double_hip'):
            self._emit(BOX, x, y, th, z0 - .35, W, D, .35, part=part, g_m=g)                                   # lower eave fascia
            self._emit(FRUSTUM, x, y, th, z0, W, D, rh * .26, w * .9, d * .86, part=part, g_m=g)              # lower skirt roof
            self._emit(BOX, x, y, th, z0 + rh * .26, w * .84, d * .8, rh * .3, part=LMK if part == LROOF else FAB, g_m=g)
            if self.det >= 1: self._emit(BOX, x, y, th, z0 + rh * .3, w * .845, d * .805, rh * .12, part=DARK, g_m=g)   # clerestory band
            self.roof(x, y, th, z0 + rh * .56, w * .84, d * .8, rh * .8, 'hip' if style == 'double_hip' else 'xieshan', part, g, o * .9, orn)
            return
        self._emit(BOX, x, y, th, z0 - .35, W, D, .35, part=part, g_m=g)                                       # eave fascia
        if style == 'hip':
            self._emit(FRUSTUM, x, y, th, z0, W, D, rh * .28, w * 1.0, d * .92, part=part, g_m=g)             # flared eave
            self._emit(FRUSTUM, x, y, th, z0 + rh * .28, w * 1.0, d * .92, rh * .72, w * .46, d * .06, part=part, g_m=g)
            rl = w * .48
        else:   # xieshan: hipped skirt + gable top
            self._emit(FRUSTUM, x, y, th, z0, W, D, rh * .38, w * .86, d * .62, part=part, g_m=g)
            self._emit(GABLE, x, y, th + math.pi / 2, z0 + rh * .38, d * .62, w * .86, rh * .62, .3, part=part, g_m=g)
            rl = w * .9
        self._emit(BOX, x, y, th, z0 + rh - .3, rl, .8, 1.0, part=part, g_m=g)                                # main ridge
        if orn:                                                                                                 # ridge-end ornaments (鸱吻)
            for k in (-1, 1):
                ex, ey = P(k * rl / 2, 0); self._emit(BOX, ex, ey, th, z0 + rh - .3, 1.1, 1.0, 2.0, part=part, g_m=g)

    # ------------------------------------------------------------------ building types
    def hall(self, x, y, th, w, d, h, roof='xieshan', z0=0, part=LMK, podium=0, g=None, cols=None, front=-1, rpart=LROOF):
        """a timber hall: podium with a stair, colonnade, walls with a dark door band, roof with eaves.
        w along local x (the facade), d in depth; the front faces local y = front (-1: 'south' for th=0)"""
        g = (self.gsite(x, y, th, w + 4, d + 4 + podium * 3.4) if podium else self.gsite(x, y, th, w, d)) if g is None else g   # (over its podium and stair)
        P = self.frame(x, y, th)
        if podium:
            self._emit(BOX, x, y, th, z0, w + 4, d + 4, podium, part=EARTH, g_m=g)
            if self.det >= 1:
                self.stair(P, 0, front * (d / 2 + 2), th, max(4, w * .3), podium, podium * 1.6, g, out=front, z0=z0)
            z0 += podium
        hb, rh = h * .56, h * .44
        if cols is None: cols = self.det >= 1 and w >= 7
        if cols:
            self._emit(BOX, x, y, th, z0, w * .82, d * .72, hb, part=part, g_m=g)
            nx, ny = max(2, round(w / 4.2)), max(2, round(d / 4.2))
            for i in range(nx + 1):
                for ly in (-d * .46, d * .46):
                    cx_, cy_ = P(-w * .48 + w * .96 * i / nx, ly); self._emit(BOX, cx_, cy_, th, z0, .65, .65, hb, part=part, g_m=g)
            for j in range(1, ny):
                for lx in (-w * .48, w * .48):
                    cx_, cy_ = P(lx, -d * .46 + d * .92 * j / ny); self._emit(BOX, cx_, cy_, th, z0, .65, .65, hb, part=part, g_m=g)
            self._emit(BOX, x, y, th, z0 + hb - .7, w * .99, d * .95, .7, part=part, g_m=g)                      # architrave
            if self.det >= 1:
                dx_, dy_ = P(0, front * (d * .36 + .08)); self._emit(BOX, dx_, dy_, th, z0 + .2, w * .62, .25, hb * .66, part=DARK, g_m=g)
        else:
            self._emit(BOX, x, y, th, z0, w, d, hb, part=part, g_m=g)
            if self.det >= 1 and w >= 4:
                dx_, dy_ = P(0, front * (d / 2 + .05)); self._emit(BOX, dx_, dy_, th, z0 + .1, min(2.4, w * .3), .2, min(3.2, hb * .7), part=DARK, g_m=g)
        self.roof(x, y, th, z0 + hb, w, d, rh, roof, part=rpart, g=g)

    def gable_house(self, x, y, th, w, d, h, part=FAB, g=None, front=-1):
        """one wing of a house: walls, a gable roof with overhang and ridge (ridge along local x, length w), door and windows
        on the front side (local y = front). On its own ground (g None) a long wing that falls more than self.step along its
        length steps down the slope in pieces, each on its own level, as on a hillside"""
        if g is None and w > 2 * d and self.site is None:   # (on a lot made one plane the wing lies along it whole)
            P = self.frame(x, y, th); fall = abs(self.ground_m(*P(w / 2, 0)) - self.ground_m(*P(-w / 2, 0)))
            k = min(int(w // (2 * d)), int(math.ceil(fall / self.step)))   # (a piece at least twice as long as it is deep)
            if k > 1:
                for i in range(k): self.gable_house(*P(w * ((i + .5) / k - .5), 0), th, w / k, d, h, part, None, front)
                return
        g = self.gsite(x, y, th, w, d) if g is None else g
        hb = h * .56
        self._emit(BOX, x, y, th, 0, w, d, hb, part=part, g_m=g)
        self.roof(x, y, th, hb, w, d, h * .44, 'gable', part=ROOF, g=g, o=.55)
        if self.det >= 1 and w >= 4:
            P = self.frame(x, y, th)
            dx_, dy_ = P(0, front * (d / 2 + .05)); self._emit(BOX, dx_, dy_, th, .1, 1.3, .2, min(2.3, hb * .8), part=DARK, g_m=g)
            if self.det >= 2 and w >= 7:
                for k in (-1, 1):
                    wx, wy = P(k * w * .3, front * (d / 2 + .05)); self._emit(BOX, wx, wy, th, hb * .35, min(1.6, w * .14), .2, hb * .32, part=DARK, g_m=g)

    def courtyard(self, x, y, th, w, d, h=6.0, part=FAB):
        """a courtyard house (合院) in a w x d lot facing south (local -y): main hall north, two side wings, a south row,
        the lot walls with a gate house at the south-east corner, a paved court and maybe a tree. On a lot made one plane
        (lot_site, fill) every building, wall and the court stand on that plane, level or tilted with the hill; alone, each
        building stands on its own ground. A lot deeper than MANSION_D is a mansion of several courts (mansion)"""
        if d > self.MANSION_D: return self.mansion(x, y, th, w, d, h, part)
        P = self.frame(x, y, th)
        md = min(8.0, d * .3); sd = min(5.5, w * .26); gd = min(4.5, d * .17)
        self.gable_house(*P(0, d / 2 - md / 2 - .4), th, w * .88, md, h * 1.1, part, front=-1)                  # 正房
        sl = d - md - gd - 3.0; cyc = (gd - md) / 2
        if sl > 4:
            self.gable_house(*P(-w / 2 + sd / 2 + .6, cyc), th + math.pi / 2, sl, sd, h * .92, part, front=-1)      # 厢房 west
            self.gable_house(*P(w / 2 - sd / 2 - .6, cyc), th + math.pi / 2, sl, sd, h * .92, part, front=1)        # 厢房 east
        self.gable_house(*P(-w * .1, -d / 2 + gd / 2 + .4), th, w * .66, gd, h * .82, part, front=1)             # 倒座
        if self.det >= 1:
            wh = 2.6
            self.strip(P(-w / 2, d / 2 - .2), P(w / 2, d / 2 - .2), .4, wh, part=part)
            self.strip(P(-w / 2 + .2, -d / 2), P(-w / 2 + .2, d / 2), .4, wh, part=part)
            self.strip(P(w / 2 - .2, -d / 2), P(w / 2 - .2, d / 2), .4, wh, part=part)
            g0, g1 = w * .24, w * .38                                                                            # gate gap, south-east
            self.strip(P(-w / 2, -d / 2 + .2), P(g0, -d / 2 + .2), .4, wh, part=part)
            self.strip(P(g1, -d / 2 + .2), P(w / 2, -d / 2 + .2), .4, wh, part=part)
            gx, gy = P((g0 + g1) / 2, -d / 2 + 1.2); g = self.gsite(gx, gy, th, g1 - g0 + .6, 2.4)
            self._emit(BOX, gx, gy, th, 0, g1 - g0 + .6, 2.4, 3.0, part=part, g_m=g)
            self.roof(gx, gy, th, 3.0, g1 - g0 + .6, 2.4, 1.4, 'gable', part=ROOF, g=g, o=.4)
            dx_, dy_ = P((g0 + g1) / 2, -d / 2 - .02); self._emit(BOX, dx_, dy_, th, .1, 1.5, .2, 2.3, part=DARK, g_m=g); self.found = 0.0
            pl = max(2, sl * .7); self.strip(P(0, cyc - pl / 2), P(0, cyc + pl / 2), w * .44, .1, part=PAVE, road=False)
            if self.rng.random() < .35:
                tx_, ty_ = P(w * .18 * (1 if self.rng.random() < .5 else -1), cyc + sl * .15)
                self.tree(tx_, ty_, 8.5, 2.6)

    MANSION_D = 60.0   # metres: a courtyard lot deeper than this is a mansion (a 95 m lot as one court is four thin halls
                       # round an empty yard, and at low detail, with no walls, an empty frame)

    def mansion(self, x, y, th, w, d, h=6.0, part=FAB):
        """a mansion (宅第, 甲第) on a large lot facing south (local -y): courts one behind another along its axis (進, about
        30 m deep each, the middle one the tallest), on a lot wider than 60 m a long side range (跨院) down each side, and one
        wall round it all with a gate on the axis, drawn at every detail: it is what tells one estate from the next"""
        P = self.frame(x, y, th)
        n = max(2, round(d / 30)); aw = w * .56 if w > 60 else w; d0 = 3.0; dk = (d - d0) / n   # (d0: room for the gate)
        for k in range(n):   # from the front court (south) to the rear
            hk = h * (1.1 if k == n // 2 else .9 if k == 0 else 1.0)
            self.courtyard(*P(0, -d / 2 + d0 + dk * (k + .5)), th, aw * .96, dk * .96, hk, part)
        if aw < w:
            sw = (w - aw) / 2
            for k in (-1, 1): self.gable_house(*P(k * (aw + sw) / 2, 0), th + math.pi / 2, d * .86, min(9.0, sw * .5), h * .85, part, front=k)
        wh, gw = 3.2, 6.0; c = [P(-w / 2, -d / 2), P(w / 2, -d / 2), P(w / 2, d / 2), P(-w / 2, d / 2)]
        for a, b in ((c[1], c[2]), (c[2], c[3]), (c[3], c[0]), (c[0], P(-gw / 2, -d / 2)), (P(gw / 2, -d / 2), c[1])): self.strip(a, b, .6, wh, part=part)
        gx, gy = P(0, -d / 2 + .8); g = self.gsite(gx, gy, th, gw + 2, 2.4)
        self._emit(BOX, gx, gy, th, 0, gw + 2, 2.4, 3.6, part=part, g_m=g)
        self.roof(gx, gy, th, 3.6, gw + 2, 2.4, 1.6, 'gable', part=ROOF, g=g, o=.4); self.found = 0.0

    def shophouses(self, a, b, depth, frontage=7.0, h=7.0, side=1, gap=.0, part=FAB, street_w=14.0, avoid=None):
        """a row of 2-storey shophouses along segment a->b (UTM), on one side (side=+1 left, -1 right), set back to the
        street's edge, roofs parallel to the street, open shop fronts and awnings toward it, a small yard behind each closed by a
        wall along the row's back. Returns the row's footprints (shop and yard).
        The houses of a row stand wall to wall at about one height (6.7 m wide shops with a gap between
        each, heights apart and bare ground behind look from behind like a row of teeth)."""
        L = math.hypot(b[0] - a[0], b[1] - a[1]); th = math.atan2(b[1] - a[1], b[0] - a[0])
        nx, ny = -math.sin(th) * side, math.cos(th) * side
        n = int(L // frontage); off = street_w / 2 + depth / 2 + .5; feet = []
        yd = min(5.0, depth * .35)   # the yard behind the house, inside the footprint (the lots around stay as they were)
        for i in range(n):
            if self.rng.random() < gap: continue
            k = (i + .5) / n; px, py = a[0] + (b[0] - a[0]) * k + nx * off, a[1] + (b[1] - a[1]) * k + ny * off
            P = self.frame(px, py, th); foot = Polygon([P(-frontage / 2, -depth / 2), P(frontage / 2, -depth / 2), P(frontage / 2, depth / 2), P(-frontage / 2, depth / 2)])
            if avoid is not None and foot.buffer(-.5).intersects(avoid): continue
            feet.append(foot); self.group()
            hh = h * (.92 + self.rng.random() * .16); g = self.gsite(px, py, th, frontage, depth)
            bx, by = px - nx * yd / 2, py - ny * yd / 2   # the house: its front on the street, the yard behind it
            self._emit(BOX, bx, by, th, 0, frontage, depth - yd, hh * .6, part=part, g_m=g)
            self.roof(bx, by, th, hh * .6, frontage, depth - yd, hh * .4, 'gable', part=ROOF, g=g, o=.5)
            self._emit(BOX, px + nx * (depth / 2 - .2), py + ny * (depth / 2 - .2), th, 0, frontage + .05, .4, 2.2, part=part, g_m=g)   # the yard's back wall
            if self.det >= 1:   # the wall between two yards (at the row's start side of each)
                yc, sd = depth / 2 - yd / 2, frontage / 2 - .15
                self._emit(BOX, px + nx * yc - math.cos(th) * sd, py + ny * yc - math.sin(th) * sd, th, 0, .3, yd, 2.0, part=part, g_m=g)
            if self.det >= 1:
                self.shopfront(px - nx * (depth / 2 + .05), py - ny * (depth / 2 + .05), th, 0, frontage * .72, 2.5, part, g)
                ax_, ay_ = px - nx * (depth / 2 + .8), py - ny * (depth / 2 + .8)
                self._emit(BOX, ax_, ay_, th, 2.9, frontage * .9, 1.6, .18, part=ROOF, g_m=g)
        return feet

    def hut(self, x, y, r=3.5, h=4.0, part=FAB):
        g = self.gsite(x, y, 0, 2 * r, 2 * r)
        self._emit(CYL, x, y, 0, 0, r, 0, h * .4, part=part, g_m=g)
        self._emit(CONE, x, y, 0, h * .4, r * 1.3, 0, h * .6, part=ROOF, g_m=g)
        if self.det >= 1:
            a = self.rng.random() * math.tau
            self._emit(BOX, x + math.cos(a) * r, y + math.sin(a) * r, a + math.pi / 2, .05, .9, .3, h * .32, part=DARK, g_m=g)

    def tree(self, x, y, h=10.0, r=3.5, kind='willow'):
        g = self.gsite(x, y, 0, 1, 1) if self.site is not None else self.ground_m(x, y)   # (in a lot made one plane: on it)
        self._emit(CYL, x, y, 0, 0, r * .12, 0, h * .35, part=TREE, g_m=g)
        k = .7 + self.rng.random() * .5
        self._emit(FRUSTUM, x, y, self.rng.random() * 3, h * .3 * k, r * 1.5 * k, r * 1.5 * k, h * .35 * k, r * 1.9 * k, r * 1.9 * k, part=TREE, g_m=g)
        self._emit(FRUSTUM, x, y, self.rng.random() * 3, h * .65 * k, r * 1.9 * k, r * 1.9 * k, h * .35 * k, r * .7 * k, r * .7 * k, part=TREE, g_m=g)

    # ------------------------------------------------------------------ Qin-Han palace types (research/qin_palaces.md, research/han_changan.md)
    def shopfront(self, x, y, th, z0, w, h, part, g):
        """an open shop front w wide on the face at (x, y): a counter (柜台) waist-high across it in the wall's colour, the dark
        opening above it up to h; a front dark from the ground up read as a black hole in the wall, not as a shop"""
        self._emit(BOX, x, y, th, z0 + .05, w, .5, .95, part=part, g_m=g)
        self._emit(BOX, x, y, th, z0 + 1.0, w, .2, max(.6, h - 1.0), part=DARK, g_m=g)

    def stair(self, P, fx, fy, th, w, h, run, g, out=-1, z0=0.0, part=EARTH):
        """a flight of steps (踏道) against a face, rising from the ground `run` out from it to `h` at the face: a few broad
        steps, each a slab from the face outward, so it reads as a stair from any side. P is the frame of what it climbs, (fx, fy)
        the middle of the face's top edge in that frame, out the side the stair leads off to (-1: local y down). (A frustum
        with its top centred over its base stood as a free blade in front of the face, not as a ramp up to it)"""
        n = max(3, min(10, round(h / 1.6)))
        for i in range(n):
            dep = run * (n - i) / n; sx, sy = P(fx, fy + out * dep / 2)
            self._emit(BOX, sx, sy, th, z0 + h * i / n, w, dep, h / n, part=part, g_m=g)

    def lean(self, x, y, th, w, d, z0, drop, part=LROOF, g=None, t=.35):
        """a lean-to roof: a thin slab w (along th) x d, its high edge on local +y at z0, falling `drop` metres to local -y"""
        dy = (-math.sin(th), math.cos(th)); k = drop / max(d, 1e-6) * self.hex / self.gex   # slope in ground metres per metre (the shear uses gex)
        s0 = self.slope; self.slope = (dy[0] * k, dy[1] * k)
        self._emit(BOX, x, y, th, z0 - drop / 2 - t, w, d, t, part=part, g_m=g); self.slope = s0

    def arcade(self, x, y, th, w, d, z0, depth=3.6, h=3.4, part=LMK, g=None, sides=(1, 1, 1, 1), bay=3.6):
        """a covered walk (回廊) around a w x d body standing at z0: posts every `bay`, a lean-to roof sloping outward from the
        body's wall. sides: south, east, north, west (local -y, +x, +y, -x)"""
        P = self.frame(x, y, th)
        for side, on in zip(('s', 'e', 'n', 'w'), sides):
            if not on: continue
            if side in 's n':
                L = w + 2 * depth; sgn = -1 if side == 's' else 1; cx_, cy_ = P(0, sgn * (d / 2 + depth / 2)); ang = th if side == 'n' else th + math.pi
            else:
                L = d; sgn = 1 if side == 'e' else -1; cx_, cy_ = P(sgn * (w / 2 + depth / 2), 0); ang = th - math.pi / 2 if side == 'e' else th + math.pi / 2
            # the roof: high against the wall, low at the posts; ang points the local +y toward the wall
            self.lean(cx_, cy_, ang, L, depth + .8, z0 + h + 1.1, 1.1, part=LROOF, g=g)
            n = max(2, int(L // bay)); Q = self.frame(cx_, cy_, ang)
            for i in range(n + 1):
                px, py = Q(-L / 2 + L * i / n, -depth / 2 + .3); self._emit(BOX, px, py, ang, z0, .55, .55, h, part=part, g_m=g)
            self._emit(BOX, *Q(0, -depth / 2 + .3), ang, z0 + h - .5, L, .6, .5, part=part, g_m=g)   # the beam on the posts

    def taixie(self, x, y, th, w, d, h, rooms=(5, 2), upper=None, mirror=0.0, part=LMK, roof_main='hip'):
        """a terrace palace (高台建筑 / 台榭) after the Qin Xianyang palace No. 1 and Yang Hongxun's reconstruction: a rammed-earth
        platform w x d, h high, with rooms let into its south and north faces (dark doors and window slits), a covered walk
        around its foot; an upper tier holding a two-storey main hall, side rooms and an open corner hall, a walk round the
        upper tier and an open terrace (露台) to the south. mirror > 0: a twin to the east across a gap of `mirror` metres,
        the two joined by a flying gallery (飞阁) at the upper level."""
        for sx in ((-1, 1) if mirror > 0 else (0,)):
            cx_, cy_ = self.frame(x, y, th)(sx * (w / 2 + mirror / 2), 0) if mirror > 0 else (x, y)
            self._taixie_one(cx_, cy_, th, w, d, h, rooms, upper, part, roof_main, flip=sx > 0)
        if mirror > 0:   # the flying gallery (飞阁) across the gap at the platform's height: a covered walk, posts and a roof
            g = self.gsite(x, y, th, mirror + 4, 7); self.found = 0.0; L_ = mirror + 8
            self._emit(BOX, x, y, th, h - .2, L_, 6.5, 1.0, part=part, g_m=g)                      # its deck
            P_ = self.frame(x, y, th); n_ = max(3, int(L_ // 4.5))
            for i in range(n_ + 1):
                for k in (-1, 1):
                    px, py = P_(-L_ / 2 + L_ * i / n_, k * 2.8); self._emit(BOX, px, py, th, h + .8, .5, .5, 3.4, part=part, g_m=g)
            self._emit(BOX, x, y, th, h + 1.6, L_ * .98, .3, 1.0, part=DARK, g_m=g)
            self.roof(x, y, th, h + 4.2, L_, 6.5, 2.2, 'gable', part=LROOF, g=g, o=1.0, ornaments=False)
            for k in (-1, 1):   # the piers that carry it over the road between the platforms
                px, py = P_(k * mirror * .22, 0); self._emit(BOX, px, py, th, 0, 3.0, 5.0, h - .2, part=EARTH, g_m=g)

    def _taixie_one(self, x, y, th, w, d, h, rooms, upper, part, roof_main, flip=False):
        """one of the twin pavilions, after Yang Hongxun's elevation and sections (research/qin_refs/ref_4): low and wide, three
        eave lines stepping down: a deep covered walk round the foot of the platform (its lean-to roof the lowest skirt, rooms
        let into the platform behind it); on the platform a ring of lower halls round a small court (the second skirt); in the
        middle the two-storey main hall, its first-floor eave and a broad hip-gable roof on top. An open terrace (露台) south."""
        P = self.frame(x, y, th); g = self.gsite(x, y, th, w, d); self.found = 0.0
        self._emit(FRUSTUM, x, y, th, 0, w, d, h, w * .96, d * .95, part=EARTH, g_m=g)
        # rooms in the platform's faces, seen as dark doors behind the walk
        for face, n in ((-1, rooms[0]), (1, rooms[1])):
            for i in range(n):
                rx = -w * .4 + w * .8 * (i + .5) / n; px, py = P(rx, face * (d / 2 * .985 + .05))
                self._emit(BOX, px, py, th, .2, min(3.2, w * .8 / n * .4), .3, min(3.6, h * .6), part=DARK, g_m=g)
        # the lowest skirt: a deep covered walk all round the foot, its roof just under the platform's edge
        self.arcade(x, y, th, w * .985, d * .975, 0, depth=5.2, h=min(4.4, h * .72), part=part, g=g, bay=4.2)
        # on the platform: the south half an open terrace with a parapet; a ring of lower halls round the north part
        uw, ud = w * .9, d * .6; uy = d * .17; z = h + .6
        ux, uy_ = P(0, uy); self._emit(BOX, ux, uy_, th, h, uw, ud, .6, part=EARTH, g_m=g)
        for k in (-1, 1):
            px, py = P(k * (w * .47), -d * .2); self._emit(BOX, px, py, th + math.pi / 2, h, d * .5, .5, 1.1, part=part, g_m=g)
        px, py = P(0, -d * .46); self._emit(BOX, px, py, th, h, w * .94, .5, 1.1, part=part, g_m=g)
        rh_ = 4.6   # the second skirt: halls along the north edge and down both sides, single storey, broad low roofs
        nx_, ny_ = P(0, uy + ud / 2 - 4.5); self.hall(nx_, ny_, th, uw, 9.0, rh_, roof='xieshan', z0=z, part=part, g=g, cols=False)
        for k in (-1, 1):
            sx_, sy_ = P(k * (uw / 2 - 4.5), uy - 2.0); self.hall(sx_, sy_, th + math.pi / 2, ud - 13.0, 9.0, rh_, roof='xieshan', z0=z, part=part, g=g, cols=False)
        # the main hall in the middle: two storeys, the first-floor eave, a broad hip-gable roof (13.4 x 12 m core at No. 1,
        # its upper storey wider with the walks round it)
        mw, md = min(uw * .48, 26.0), min(ud * .55, 17.0); mx, my = P(0, uy - 1.0)
        self._emit(BOX, mx, my, th, z, mw, md, 5.6, part=part, g_m=g)
        if self.det >= 1:
            for k in (-1, 0, 1):
                dx_, dy_ = P(k * mw * .25, uy - 1.0 - md / 2 - .05); self._emit(BOX, dx_, dy_, th, z + .3, 2.2, .25, 3.6, part=DARK, g_m=g)
        self.roof(mx, my, th, z + 5.6, mw, md, 1.6, 'flat', part=LROOF, g=g, o=2.4)   # the first floor's eave, deep
        self._emit(BOX, mx, my, th, z + 6.2, mw * .78, md * .78, 4.0, part=part, g_m=g)
        if self.det >= 1: self._emit(BOX, mx, my, th, z + 7.6, mw * .79, md * .79, 1.2, part=DARK, g_m=g)
        self.roof(mx, my, th, z + 10.2, mw * .78, md * .78, 3.8, 'xieshan' if roof_main == 'hip' else roof_main, part=LROOF, g=g, o=2.0)
        for b in (upper or []):   # extra halls in the platform's frame: (fx, fy, w, d, h, roof)
            bx, by = P(b[0] * w, b[1] * d); self.hall(bx, by, th, b[2], b[3], b[4], roof=b[5], z0=z, part=part, g=g)
        # a stair up the south face, toward the twin's side
        self.stair(P, -w * .3 if not flip else w * .3, -d * .95 / 2, th, 5.0, h * .98, d * .025 + 5.2 + h * 1.05, g)

    def front_hall(self, x, y, th, w=200.0, d=400.0, tiers=((140, 200, 3.0), (120, 180, 8.0), (110, 165, 15.0)), part=LMK):
        """the front hall of Weiyang (未央宫前殿, han_changan.md §4-B): a platform rising in three terraces from south to north
        (each n-s depth, e-w width, height); on each a great hall at its north side and a walled court in front of it; rooms
        let into the terraces' faces with single-slope roofs (the 46 rooms of area A). w x d: the whole platform."""
        P = self.frame(x, y, th); y0 = -d / 2
        for i, (td, tw, th_) in enumerate(tiers):
            cy = y0 + td / 2; tx, ty = P(0, cy); self.group()
            g = self.gsite(tx, ty, th, tw, td)
            self._emit(FRUSTUM, tx, ty, th, 0, tw, td, th_, tw * .985, td * .98, part=EARTH, g_m=g); self.found = 0.0   # footed down the slope
            if self.det >= 1:   # rooms in the terrace's east and west faces, their lean-to roofs, a walk in front
                for k in (-1, 1):
                    n = max(4, int(td // 9))
                    for j in range(n):   # (kept clear of the tiers' junctions: the rooms of two tiers never meet)
                        ry = cy - td / 2 + 6 + (td - 12) * (j + .5) / n; rx, ryy = P(k * (tw / 2 + 2.6), ry); gr = self.gsite(rx, ryy, th, 5.2, (td - 12) / n); self.found = 0.0
                        self._emit(BOX, rx, ryy, th, 0, 5.2, (td - 12) / n * .92, min(4.2, th_ + 1), part=part, g_m=gr)
                        dx_, dy_ = P(k * (tw / 2 + 5.25), ry); self._emit(BOX, dx_, dy_, th, .2, .3, 2.0, 2.6, part=DARK, g_m=gr)
                    lx, ly = P(k * (tw / 2 + 3.2), cy); gl_ = self.gsite(lx, ly, th, 7.2, td); self.found = 0.0
                    self.lean(lx, ly, th + (math.pi / 2 if k > 0 else -math.pi / 2), td, 7.2, min(4.2, th_ + 1) + 1.2, 1.4, g=gl_)
            # the court on this terrace (south) and its hall (north); the top hall double-roofed
            z = th_; hd_ = min(td * .32, 40.0); hw_ = min(tw * .55, 110.0) if i == len(tiers) - 1 else min(tw * .45, 90.0)
            hx, hy = P(0, cy + td / 2 - hd_ / 2 - 8)
            self.hall(hx, hy, th, hw_, hd_, 18 if i == len(tiers) - 1 else 14, roof='double_hip' if i == len(tiers) - 1 else 'hip', z0=z, part=part, g=g, podium=1.6)
            cw, cd = tw * .8, td - hd_ - 24; cx_, cyy = P(0, cy - td / 2 + cd / 2 + 6)
            for (a_, b_) in (((-cw / 2, -cd / 2), (cw / 2, -cd / 2)), ((-cw / 2, -cd / 2), (-cw / 2, cd / 2)), ((cw / 2, -cd / 2), (cw / 2, cd / 2))):
                A = self.frame(cx_, cyy, th)(*a_); B = self.frame(cx_, cyy, th)(*b_); self.strip(A, B, 3.0, 3.2, part=part, z0=z, g=g)
            if self.det >= 1:
                gx_, gy_ = self.frame(cx_, cyy, th)(0, -cd / 2); self.hall(gx_, gy_, th, 26, 9, 9, roof='hip', z0=z, part=part, g=g, cols=False)
            # a stair from the terrace below (or the ground) up its south face
            sx, sy = P(0, cy - td / 2 - th_ * .55); gs_ = min(self.ground_m(sx, sy), g); self.stair(P, 0, cy - td / 2, th, 14, th_ * .98 + (g - gs_), th_ * 1.3, gs_)
            y0 += td   # the next terrace north of this one (they were all stacked at the south end)

    def court(self, x, y, th, w, d, main=(0.6, .2, 14, 'hip'), north=None, wings=True, wall_h=4.0, part=LMK, podium=1.2):
        """a walled palace or office court (椒房殿, 少府, 中央官署 ...): an enclosure with a gate hall, the main hall (w frac, d frac,
        height, roof) on a podium at the north of the court behind a paved yard, an optional rear hall, side wings facing the
        yard, a covered walk round the yard"""
        P = self.frame(x, y, th)   # each hall on its own ground, the walls and the yard along the slope (as courtyard)
        cs = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]; gw = max(8.0, w * .12)
        for i in range(4):
            (ax, ay), (bx, by) = cs[i], cs[(i + 1) % 4]
            for (sx, sy), (ex, ey) in ([((ax, ay), (-gw / 2 - 2, ay)), ((gw / 2 + 2, ay), (bx, by))] if i == 0 else [((ax, ay), (bx, by))]):
                self.strip(P(sx, sy), P(ex, ey), 1.6, wall_h, part=part)
                if self.det >= 1: self.strip(P(sx, sy), P(ex, ey), 2.4, .5, part=LROOF, z0=wall_h)
        gx_, gy_ = P(0, -d / 2); self.hall(gx_, gy_, th, gw * 1.8, 8, 8, roof='gable', part=part, cols=False)
        mw, md = w * main[0], d * main[1]; mx, my = P(0, d / 2 - md / 2 - (d * .22 if north else 8))
        self.hall(mx, my, th, mw, md, main[2], roof=main[3], part=part, podium=podium)
        if north:
            nw_, nd_ = w * north[0], d * north[1]; nx, ny = P(0, d / 2 - nd_ / 2 - 5); self.hall(nx, ny, th, nw_, nd_, north[2], roof=north[3], part=part, podium=podium * .6)
        yd = d - md - 30 - (d * .22 if north else 0)
        if wings and self.det >= 1 and yd > 12:
            for k in (-1, 1):
                wx, wy = P(k * (w / 2 - 6), -d / 2 + 14 + yd / 2); self.hall(wx, wy, th + math.pi / 2, yd * .8, 8, 7, roof='gable', part=part, cols=False, front=k)
        if self.det >= 1:
            yl = max(4, yd * .8); self.strip(P(0, -d / 2 + 14 + yd / 2 - yl / 2), P(0, -d / 2 + 14 + yd / 2 + yl / 2), w * .5, .12, part=PAVE, road=False)
        self.found = 0.0

    def armoury(self, x, y, th, w=710.0, d=322.0, part=LMK):
        """the arsenal (武库, han_changan.md §9): a walled enclosure split by a cross wall into east and west yards, seven long
        storehouses (4 east, 3 west); each a rammed-earth hall on a 2.8 m base, thick walls, cross walls into rooms (each with
        its own roof), doors on the long sides, a walk in front. No. 7 (west yard) 234 x 45.7 m, four rooms."""
        P = self.frame(x, y, th)
        cs = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
        for i in range(4): self.strip(P(*cs[i]), P(*cs[(i + 1) % 4]), 3.0, 5.0, part=part)
        self.strip(P(-w * .1, -d / 2), P(-w * .1, d / 2), 3.0, 5.0, part=part)   # the cross wall
        houses = [(-w * .32, 0, 234, 45.7, 4)] + [(-w * .32, k * d * .3, 160, 26, 3) for k in (-1, 1)] + [(w * (.12 + .21 * j), k * d * .22, 120, 24, 3) for j in (0, 1) for k in (-1, 1)]
        for hx, hy, L, D, n in houses:
            self.group(); cx_, cy_ = P(hx, hy); gg = self.gsite(cx_, cy_, th, L, D)
            self._emit(BOX, cx_, cy_, th, 0, L + 4, D + 4, 1.4, part=EARTH, g_m=gg); self.found = 0.0   # the base, footed down the slope
            for j in range(n):
                rx, ry = self.frame(cx_, cy_, th)(-L / 2 + L * (j + .5) / n, 0)
                self._emit(BOX, rx, ry, th, 1.4, L / n - 1.5, D, 6.0, part=part, g_m=gg)
                self.roof(rx, ry, th, 7.4, L / n - 1.5, D, 5.0, 'hip', part=LROOF, g=gg, ornaments=False)
                if self.det >= 1:
                    for kk in (-1, 1):
                        dx_, dy_ = self.frame(rx, ry, th)(0, kk * (D / 2 + .05)); self._emit(BOX, dx_, dy_, th, 1.6, 2.1, .3, 3.4, part=DARK, g_m=gg)
            if self.det >= 1: self.lean(*self.frame(cx_, cy_, th)(0, -D / 2 - 2.2), th, L, 4.4, 5.4, 1.0, g=gg)

    def market(self, x, y, th, w, d, part=LMK, lanes=2):
        """a market (市, han_changan.md §10): a walled square with gates on each side, a grid of lanes (井 shape, schematic),
        long rows of shops (列肆) filling every block between the lanes, back to back under one roof with an alley between one
        row and the next (rows along the lanes alone leave a 200 m block an empty square), and the market
        tower (旗亭, 市楼 皆重屋) at the centre"""
        P = self.frame(x, y, th)
        cs = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
        for i in range(4):
            (ax, ay), (bx, by) = cs[i], cs[(i + 1) % 4]; mxx, myy = (ax + bx) / 2, (ay + by) / 2; ux, uy = (bx - ax), (by - ay); Lw = math.hypot(ux, uy); ux, uy = ux / Lw, uy / Lw
            self.strip(P(ax, ay), P(mxx - ux * 9, myy - uy * 9), 3.0, 4.5, part=part); self.strip(P(mxx + ux * 9, myy + uy * 9), P(bx, by), 3.0, 4.5, part=part)
        xs = [-w / 2 + w * (i + 1) / (lanes + 1) for i in range(lanes)]; ys = [-d / 2 + d * (i + 1) / (lanes + 1) for i in range(lanes)]
        for lx in xs: self.strip(P(lx, -d / 2), P(lx, d / 2), 12, .12, part=PAVE)
        for ly in ys: self.strip(P(-w / 2, ly), P(w / 2, ly), 12, .12, part=PAVE)
        bx, by = [-w / 2] + xs + [w / 2], [-d / 2] + ys + [d / 2]
        for i in range(len(bx) - 1):   # each block: rows of shops 14 m deep (two back to back), an alley of 10 m between rows,
            for j in range(len(by) - 1):   # a row broken every 40 m or so by a cross alley; 9 m off a lane's centre, 6 m off the wall
                x0_, x1_ = bx[i] + (9 if i else 6), bx[i + 1] - (9 if i < len(bx) - 2 else 6)
                y0_, y1_ = by[j] + (9 if j else 6), by[j + 1] - (9 if j < len(by) - 2 else 6)
                nr = int((y1_ - y0_ + 10) // 24); Lx = x1_ - x0_
                if nr < 1 or Lx < 20: continue
                ns = max(1, round(Lx / 40)); sl = (Lx - 6 * (ns - 1)) / ns; oy = y0_ + (y1_ - y0_ - (nr * 24 - 10)) / 2
                for r_ in range(nr):
                    ry = oy + 7 + r_ * 24
                    for s_ in range(ns):
                        sx = x0_ + s_ * (sl + 6) + sl / 2
                        if abs(sx) < sl / 2 + 12 and abs(ry) < 7 + 12: continue   # (the tower's square)
                        self.group(); px_, py_ = P(sx, ry); gg = self.gsite(px_, py_, th, sl, 14)
                        self._emit(BOX, px_, py_, th, 0, sl, 14, 4.0, part=FAB, g_m=gg)
                        self.roof(px_, py_, th, 4.0, sl, 14, 2.2, 'gable', part=ROOF, g=gg, o=.6)
                        if self.det >= 1:   # the open shop fronts, both sides
                            for k in (-1, 1): fx_, fy_ = P(sx, ry + k * 7.05); self._emit(BOX, fx_, fy_, th, .1, sl * .9, .2, 2.6, part=DARK, g_m=gg)
                        self.found = 0.0
        self.group(); tx_, ty_ = P(0, 0); gg = self.gsite(tx_, ty_, th, 18, 18)   # the market tower, several storeys
        for i, (sz, hh) in enumerate(((18, 5.0), (14, 4.2), (11, 3.8))):
            z0 = sum(q[1] + 1.6 for q in ((18, 5.0), (14, 4.2), (11, 3.8))[:i])
            self._emit(BOX, tx_, ty_, th, z0, sz, sz, hh, part=part, g_m=gg); self.found = 0.0
            self.roof(tx_, ty_, th, z0 + hh, sz, sz, 1.6 if i < 2 else 3.4, 'flat' if i < 2 else 'hip', part=LROOF, g=gg, ornaments=False)

    def kiln(self, x, y, a, r=3.2, g=None):
        """a kiln: a low earth dome with its stoking mouth (dark) facing direction a (radians)"""
        g = self.ground_m(x, y) if g is None else g; q = r / 3.2
        self._emit(CYL, x, y, 0, 0, r, 0, 2.2 * q, part=EARTH, g_m=g); self._emit(CONE, x, y, 0, 2.2 * q, 3.4 * q, 0, 2.4 * q, part=EARTH, g_m=g)
        if self.det >= 1: self._emit(BOX, x + r * math.cos(a), y + r * math.sin(a), a, .05, 1.2 * q, .4, 1.4 * q, part=DARK, g_m=g)

    def workshops(self, x, y, th, w, d, kilns=33, part=FAB):
        """a craft quarter laid out as excavated in Han Chang'an's north-west corner (han_changan.md §10, WS26: pottery-figure
        kilns in the west and the north-centre, an iron foundry in the south-centre, a mint in the north-east): walled yards on
        a grid of 10 m lanes, each one trade's: a row of kilns with a work shed and a drying floor; a furnace, four mould kilns,
        a casting shed and scrap pits; a mint of two halls and a store. Yards no trade claims are the workers' houses. Scattered
        kilns read as dots from any distance"""
        P = self.frame(x, y, th); nc, nr = max(2, round(w / 85)), max(2, round(d / 70)); cw, ch = w / nc, d / nr
        cells = [(i, j) for i in range(nc) for j in range(nr)]; at = lambda c: ((c[0] + .5) / nc, (c[1] + .5) / nr)   # 0..1 from the west, the south
        near = lambda fx, fy: min(cells, key=lambda c: (at(c)[0] - fx) ** 2 + (at(c)[1] - fy) ** 2)
        mint, foundry = near(.85, .85), near(.5, .15)
        pottery = [c for c in cells if c not in (mint, foundry) and (at(c)[0] < .4 or at(c)[1] > .6)]
        per = [kilns // len(pottery) + (1 if q < kilns % len(pottery) else 0) for q in range(len(pottery))] if pottery else []
        for c in cells:
            cx_, cy_ = -w / 2 + cw * (c[0] + .5), -d / 2 + ch * (c[1] + .5); yw, yd = cw - 10, ch - 10; Q = self.frame(*P(cx_, cy_), th)
            if c not in pottery and c not in (mint, foundry):   # the workers' houses
                self.fill(Polygon([Q(u * yw / 2, v * yd / 2) for u, v in ((-1, -1), (1, -1), (1, 1), (-1, 1))]), th, (18.0, 16.0), 'dwelling', 4.5, .15, part=part)
                continue
            self.group()
            cn = [Q(-yw / 2, -yd / 2), Q(yw / 2, -yd / 2), Q(yw / 2, yd / 2), Q(-yw / 2, yd / 2)]   # the yard wall, its gate in the south side
            for a_, b_ in ((cn[1], cn[2]), (cn[2], cn[3]), (cn[3], cn[0]), (cn[0], Q(-3, -yd / 2)), (Q(3, -yd / 2), cn[1])): self.strip(a_, b_, .8, 2.4, part=part)
            south = th - math.pi / 2
            if c in pottery:   # kilns along the north wall, mouths south; the shed down the west side; the drying floor between
                k_ = per[pottery.index(c)]
                for m in range(k_): self.kiln(*Q(-yw * .3 + yw * .6 * (m + .5) / k_, yd / 2 - 7), south)
                self.gable_house(*Q(-yw / 2 + 6, -4), th + math.pi / 2, yd * .6, 7, 4.5, part, front=-1)
                self.strip(Q(yw * .05, -yd * .3), Q(yw * .05, yd * .15), yw * .45, .1, part=PAVE, road=False)
            elif c == foundry:   # the furnace, four mould-drying kilns, the casting shed along the south, eight scrap pits
                fx_, fy_ = Q(-yw * .15, yd * .2); g_ = self.ground_m(fx_, fy_)
                self._emit(CYL, fx_, fy_, 0, 0, 4.5, 0, 5.5, part=EARTH, g_m=g_); self._emit(CONE, fx_, fy_, 0, 5.5, 4.6, 0, 3.0, part=EARTH, g_m=g_)
                self._emit(CYL, fx_, fy_, 0, 8.5, 1.0, 0, 3.0, part=EARTH, g_m=g_)
                for m in range(4): self.kiln(*Q(yw * .12 + m * 7, yd * .25), south, r=2.4)
                self.gable_house(*Q(0, -yd / 2 + 9), th, yw * .62, 9, 5.5, part, front=1)
                for m in range(8): self._emit(BOX, *Q(-yw * .4 + (m % 4) * 6.5, -yd * .05 + (m // 4) * 6), th, 0, 4, 3, .12, part=DARK)
            else:   # the mint: two halls on the axis and a store
                self.gable_house(*Q(0, yd * .25), th, yw * .55, 10, 6.5, part, front=-1)
                self.gable_house(*Q(0, -yd * .12), th, yw * .45, 9, 6, part, front=-1)
                self.gable_house(*Q(yw * .36, 0), th + math.pi / 2, yd * .45, 7, 5, part, front=1)
            self.found = 0.0

    def ward(self, region, th, lot=(22.0, 28.0), h=6.0, wall_h=3.5, empty=.08, avoid=None):
        """a walled ward (闾里, han_changan.md §11-12F: no excavated ward; the walls, two gates and the cross lane follow the texts,
        the houses the Han courtyard types): its wall with a gate (闾门) in the north and south sides, a cross of lanes, the
        lots filled with small courtyard houses (一堂二内, 曲尺形, 三合院)"""
        if region.is_empty: return
        minx, miny, maxx, maxy = region.bounds; cx_, cy_ = (minx + maxx) / 2, (miny + maxy) / 2
        ring = list(region.exterior.coords)
        for a, b in zip(ring[:-1], ring[1:]):
            mx_, my_ = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; horiz = abs(b[1] - a[1]) < abs(b[0] - a[0])
            if horiz:   # north and south sides: a gate gap in the middle
                L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                self.strip(a, (mx_ - ux * 4, my_ - uy * 4), 1.2, wall_h, part=FAB); self.strip((mx_ + ux * 4, my_ + uy * 4), b, 1.2, wall_h, part=FAB)
                self.group(); gg = self.gsite(mx_, my_, th, 9, 4); self._emit(BOX, mx_, my_, th, 0, 9, 4, 4.4, part=WALL, g_m=gg); self.found = 0.0
                self.roof(mx_, my_, th, 4.4, 9, 4, 1.8, 'gable', part=ROOF, g=gg, o=.4); self._emit(BOX, mx_, my_, th, .1, 3, 4.4, 3.0, part=DARK, g_m=gg)
            else: self.strip(a, b, 1.2, wall_h, part=FAB)
        inside_ = region.buffer(-3.5)   # the lanes stop at the ward wall
        for ln_, w_ in ((LineString([(cx_, miny), (cx_, maxy)]), 6), (LineString([(minx, cy_), (maxx, cy_)]), 5)):
            for sg in _lines(ln_.intersection(inside_)):
                c_ = list(sg.coords); self.strip(c_[0], c_[-1], w_, .1, part=PAVE)
        lanes = shapely.union_all([LineString([(cx_, miny), (cx_, maxy)]).buffer(5), LineString([(minx, cy_), (maxx, cy_)]).buffer(4.5)])
        inner = region.buffer(-3).difference(lanes)
        if avoid is not None and not avoid.is_empty: inner = inner.difference(avoid)
        self.fill(inner, th, lot, 'courtyard', h, empty)

    def terrace(self, x, y, th, w, d, h, tiers=3, top=.55, halls=(), part=LMK, stairs=True, gallery=True):
        """a rammed-earth stepped platform (高台) with halls on top; a stair on the south face, roofed walks on the tiers"""
        g = self.gsite(x, y, th, w, d); P = self.frame(x, y, th)
        sides = ((-1, -1, 1, -1), (1, -1, 1, 1), (1, 1, -1, 1), (-1, 1, -1, -1))
        for i in range(tiers):
            k0 = 1 - (1 - top) * i / tiers; k1 = 1 - (1 - top) * (i + 1) / tiers
            self._emit(FRUSTUM, x, y, th, h * i / tiers, w * k0, d * k0, h / tiers, w * k1 * .985, d * k1 * .985, part=EARTH, g_m=g)
            if self.det >= 1 and i < tiers - 1:   # a roofed walk along each lower tier
                kk = (k1 + k0) / 2 * .97
                for (lx0, ly0, lx1, ly1) in sides:
                    self.strip(P(lx0 * w * kk / 2, ly0 * d * kk / 2), P(lx1 * w * kk / 2, ly1 * d * kk / 2), 2.6, 2.4, part=LROOF, z0=h * (i + 1) / tiers, g=g)
        if stairs:
            sw = max(6, w * .1)
            self.stair(P, 0, -d * top / 2, th, sw, h * .98, d * (1 - top) / 2 + h * 1.05, g)
        tw, td = w * top, d * top
        if gallery and self.det >= 1:   # a corridor ring on the top edge
            for (lx0, ly0, lx1, ly1) in sides:
                a = P(lx0 * tw * .47, ly0 * td * .47); b = P(lx1 * tw * .47, ly1 * td * .47)
                L = math.hypot(b[0] - a[0], b[1] - a[1]); ang = math.atan2(b[1] - a[1], b[0] - a[0]); m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                self._emit(BOX, m[0], m[1], ang, h, L, 3.4, 3.0, part=LMK, g_m=g)
                self.roof(m[0], m[1], ang, h + 3.0, L, 3.4, 1.8, 'gable', part=LROOF, g=g, o=.6, ornaments=False)
        for hx, hy, hw, hd, hh, roof in halls:   # hall offsets in the terrace's local frame, fractions of the top size
            px, py = P(hx * tw, hy * td)
            self.hall(px, py, th, hw * tw, hd * td, hh, roof=roof, z0=h, part=LMK, g=g, podium=1.2)

    def walkway(self, a, b, h=8.0, w=5.0, part=LMK, piece=60.0):
        """an elevated covered corridor (复道) on posts: the deck runs h above the ground, laid along the slope piece by piece
        (lay), so a corridor climbing the north slope rises with it smoothly; each post stands on its own ground"""
        L = math.hypot(b[0] - a[0], b[1] - a[1]); th = math.atan2(b[1] - a[1], b[0] - a[0])
        if L < 2: return
        n = max(1, math.ceil(L / piece)); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        for j in range(n):
            p = (a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n); q = (a[0] + (b[0] - a[0]) * (j + 1) / n, a[1] + (b[1] - a[1]) * (j + 1) / n)
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2; Lp = L / n + .2
            self.group(); g, self.slope, _ = self.lay(p, q, w)
            self._emit(BOX, mx, my, th, h, Lp, w, 1.2, part=part, g_m=g)
            if self.det >= 1: self._emit(BOX, mx, my, th, h + 1.2, Lp, w * .9, 2.0, part=DARK, g_m=g)
            self.roof(mx, my, th, h + 3.2, Lp, w, 1.8, 'gable', part=LROOF, g=g, o=.7, ornaments=False)
            sl = self.slope; self.slope = None
            m_ = max(2, int(Lp // 12))
            for i in range(m_ + (1 if j == n - 1 else 0)):   # each post from its own ground up to the deck above it
                k = i / m_; qx, qy = p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k; gq = self.ground_m(qx, qy)
                deck = g + sl[0] * (qx - mx) + sl[1] * (qy - my)
                self._emit(BOX, qx, qy, th, 0, 1.2, w * .8, h + max(0.0, deck - gq), part=part, g_m=gq)

    def pagoda(self, x, y, h=40.0, w=12.0, storeys=7, part=LMK):
        g = self.gsite(x, y, 0, w * 1.5, w * 1.5)
        self._emit(BOX, x, y, 0, 0, w * 1.5, w * 1.5, 2.0, part=EARTH, g_m=g)
        z = 2.0
        for i in range(storeys):
            k = 1 - .45 * i / storeys; sh = (h - 2) * .9 / storeys
            self._emit(BOX, x, y, 0, z, w * k, w * k, sh * .72, part=part, g_m=g)
            if self.det >= 1: self._emit(BOX, x, y, 0, z + sh * .25, w * k * .3, w * k + .2, sh * .3, part=DARK, g_m=g)
            self._emit(FRUSTUM, x, y, 0, z + sh * .72, w * k * 1.38, w * k * 1.38, sh * .28, w * k * .92, w * k * .92, part=LROOF, g_m=g)
            z += sh
        self._emit(CYL, x, y, 0, z, w * .08, 0, h * .1, part=LROOF, g_m=g)
        self._emit(CONE, x, y, 0, z, w * .22, 0, h * .06, part=LROOF, g_m=g)

    def bell_tower(self, x, y, th=0.0, w=22.0, part=LMK):
        g = self.gsite(x, y, th, w, w)
        self._emit(BOX, x, y, th, 0, w, w, 9, part=WALL, g_m=g)
        if self.det >= 1:   # passages through the base in both directions
            self._emit(BOX, x, y, th, 0, 5, w + .4, 5.5, part=DARK, g_m=g)
            self._emit(BOX, x, y, th, 0, w + .4, 5, 5.5, part=DARK, g_m=g)
        self._emit(BOX, x, y, th, 9, w + .4, w + .4, .9, part=WALL, g_m=g)
        self.hall(x, y, th, w * .66, w * .66, 15, roof='double', z0=9.9, part=part, g=g)

    def paifang(self, x, y, th, w=12.0, h=8.0):
        """a memorial archway: four posts, a beam, three small roofs"""
        g = self.gsite(x, y, th, w, 1.0); P = self.frame(x, y, th)
        for k in (-.5, -.17, .17, .5):
            px, py = P(k * w, 0); self._emit(BOX, px, py, th, 0, .9, .9, h * .78, part=LMK, g_m=g)
        self._emit(BOX, x, y, th, h * .6, w * 1.04, .9, h * .14, part=LMK, g_m=g)
        self.roof(x, y, th, h * .78, w * .36, 1.4, h * .2, 'hip', part=LROOF, g=g, o=.5, ornaments=False)
        for k in (-1, 1):
            rx, ry = P(k * w * .34, 0); self.roof(rx, ry, th, h * .7, w * .3, 1.2, h * .16, 'hip', part=LROOF, g=g, o=.4, ornaments=False)

    def compound(self, x, y, th, w, d, halls, wall_h=4.0, part=LMK, side_halls=True):
        """a walled compound (temple, office, palace court): enclosure wall with a tiled coping, a gate hall, halls on the
        axis on podiums, side halls facing the axis, a paved axis and a few trees.
        halls: list of (ly fraction -0.5..0.5 along the axis, w fraction, d fraction, h, roof)"""
        if max(w, d) > self.COURT_M: return self._compound(x, y, th, w, d, halls, wall_h, part, side_halls)   # a palace city: its halls on their own ground, its walls along the hill
        with self.lot_site(x, y, th, w, d):   # one court, one plane: its halls, gate, walls and paving on it (on a steep slope, on a platform)
            self._compound(x, y, th, w, d, halls, wall_h, part, side_halls)

    COURT_M = 300.0   # metres: a walled court up to this size is built on one plane (lot_site); a palace city of a kilometre or two
                      # spans more ground than one plane can follow, so its halls stand each on its own level

    def _compound(self, x, y, th, w, d, halls, wall_h, part, side_halls):
        P = self.frame(x, y, th)
        corners = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
        gw = max(6.0, min(40.0, w * .16))
        for i in range(4):
            (ax, ay), (bx, by) = corners[i], corners[(i + 1) % 4]
            segs = [((ax, ay), (bx, by))]
            if i == 0: segs = [((ax, ay), (-gw * .8 - .3, ay)), ((gw * .8 + .3, ay), (bx, by))]   # south wall: it stops at the gate hall
            for (sx, sy), (ex, ey) in segs:
                a, b = P(sx, sy), P(ex, ey)
                self.strip(a, b, 1.4, wall_h, part=part)
                if self.det >= 1: self.strip(a, b, 2.0, .45, part=LROOF, z0=wall_h)
        gx, gy = P(0, -d / 2)
        self.hall(gx, gy, th, gw * 1.6, max(6, gw * .7), min(14, wall_h * 2.1), roof='xieshan', part=part, cols=False)
        aw = max(3, min(12, w * .08))
        if self.det >= 1:   # the paved axis
            self.strip(P(0, -d / 2 + 2), P(0, d / 2 - 2), aw, .12, part=PAVE)
        clear = [(0, -d / 2, gw * .8, max(3, gw * .35)), (0, 0, aw / 2, d / 2)]   # (local centre, half sizes): no tree there
        for n_, (ly, fw, fd, hh, roof) in enumerate(halls):
            hx, hy = P(0, ly * d); pod = max(.8, hh * .12)
            self.hall(hx, hy, th, fw * w, fd * d, hh, roof=roof, z0=0, part=part, podium=pod, g=None)   # (on the court's plane)
            clear.append((0, ly * d, fw * w / 2 + 2, fd * d / 2 + 2 + pod * 1.6))   # its podium and the stair before it
            if side_halls and self.det >= 1 and n_ > 0:
                sl = min(max(8, fd * d * 1.4), d - 10); sw_ = min(8, w * .14)
                cy_ = min(max((ly - .14) * d, -d / 2 + sl / 2 + 4), d / 2 - sl / 2 - 4)   # inside the walls (a hall near the gate had its side halls half outside them)
                for k in (-1, 1):
                    sx, sy = P(k * (w / 2 - sw_ / 2 - 2.5), cy_)
                    self.hall(sx, sy, th + math.pi / 2, sl, sw_, hh * .65, roof='gable', part=part, g=None, cols=False, front=k)
                    clear.append((k * (w / 2 - sw_ / 2 - 2.5), cy_, sw_ / 2, sl / 2))
        if self.det >= 1 and w * d < 60000:   # a few trees in the courts, never in a hall, its podium or stair, the gate or the axis
            for _ in range(int(w * d / 1800)):
                lx, ly_ = self.rng.uniform(-.42, .42) * w, self.rng.uniform(-.42, .42) * d
                if any(abs(lx - cx_) < hx_ + 5 and abs(ly_ - cy_) < hy_ + 5 for cx_, cy_, hx_, hy_ in clear):   # (5 m: the crown)
                    for _ in range(3): self.rng.random()   # the draws tree() would take: the rest of the city stays as it was
                    continue
                self.tree(*P(lx, ly_), 9, 3)

    def factory(self, x, y, th, w, d, bays=8, h=10.0, part=LMK):
        """a saw-tooth weaving shed: a long body, a row of north-light roofs, window bands on the long walls"""
        g = self.gsite(x, y, th, w, d); P = self.frame(x, y, th)
        self._emit(BOX, x, y, th, 0, w, d, h * .6, part=part, g_m=g)
        if self.det >= 1:
            for z in (h * .15, h * .38): self._emit(BOX, x, y, th, z, w * .97, d + .3, h * .1, part=DARK, g_m=g)
        bw = w / bays
        for i in range(bays):
            px, py = P(-w / 2 + bw * (i + .5), 0)
            self._emit(FRUSTUM, px, py, th, h * .6, bw, d, h * .4, bw * .1, d * .98, part=ROOF, g_m=g)
            if self.det >= 1:
                gx_, gy_ = P(-w / 2 + bw * (i + .5) + bw * .38, 0); self._emit(BOX, gx_, gy_, th, h * .6, bw * .12, d * .96, h * .36, part=DARK, g_m=g)

    def chimney(self, x, y, h=55.0, r=2.5, part=LMK):
        self._emit(FRUSTUM, x, y, 0, 0, r * 2.4, r * 2.4, h, r * 1.4, r * 1.4, part=part)
        if self.det >= 1:
            for z in (h * .3, h * .62, h * .9):
                k = r * 2.4 * (1 - z / h * .42) + .2; self._emit(BOX, x, y, 0, z, k, k, .8, part=DARK)

    def slab(self, x, y, th, w=60.0, d=12.0, h=14.0, part=FAB):
        """a Soviet-style dormitory block: a window in every 3.6 m bay of each floor on both long sides, a low hip roof (a dark
        band round every floor read as a striped cabinet, not as rooms)"""
        g = self.gsite(x, y, th, w, d)
        self._emit(BOX, x, y, th, 0, w, d, h, part=part, g_m=g)
        if self.det >= 1:
            P = self.frame(x, y, th); nb = max(1, int(w // 3.6))
            for f in range(int(h // 3.2)):
                for i in range(nb):
                    for side in (-1, 1):
                        wx, wy = P(-w / 2 + w * (i + .5) / nb, side * d / 2)
                        self._emit(BOX, wx, wy, th, 1.2 + f * 3.2, 1.6, .3, 1.4, part=DARK, g_m=g)
        self.roof(x, y, th, h, w, d, 2.6, 'hip', part=ROOF, g=g, o=.5, ornaments=False)

    # ------------------------------------------------------------------ house types from the sources (house_types: types/, city.yaml)
    def house(self, x, y, th, lw, ld, T, part=FAB):
        """a house of a declared type T (house_types) on a lw x ld lot whose street side is local -y. A margin keeps lots apart;
        the front leaves room for a portico and a podium's stair. detached: one building set back in its yard; row: wall to wall
        with its neighbours, a yard behind; court: one building round a court (a block of flats round a light well, a house
        round its atrium or patio), on one level; compound: separate buildings round a yard inside a wall, the main one at the
        back, each on its own ground"""
        P = self.frame(x, y, th); j = self.rng.random; m = .15
        n = self.rng.randint(*T['storeys']); pm, pz = T['portico_m'], T['podium_m']
        front = m + pm + pz * 1.4   # (the stair before a podium)
        W, D = lw - 2 * m, ld - m - front   # the room the buildings have
        f = T['form']; R = T['roof']; along = R.get('ridge', 'along') == 'along'
        if f == 'detached':
            w, d = W * (.62 + .1 * j()), D * (.5 + .08 * j()); s = max(0.0, (ld - 2 * m) * .1 - pm)
            self.house_body(*P(0, -ld / 2 + front + s + d / 2), th, w, d, n, T, part, along=along)
            if T['yard_wall_m'] and self.det >= 1: self._yard_wall(P, lw, ld, m, T['yard_wall_m'], part)
        elif f == 'row':   # (no eaves past the party walls: two neighbours' roofs at one height would overlap and flicker)
            d = D * (.6 + .06 * j())
            self.house_body(*P(0, -ld / 2 + front + d / 2), th, W, d, n, T, part, along=along, ends=False)
            if T['yard_wall_m'] and self.det >= 1:   # the yard's back wall and the wall to the next yard
                yb = ld / 2 - m - .2; y0_ = -ld / 2 + front + d; g = self.gsite(*P(0, (y0_ + yb) / 2), th, W, yb - y0_)
                self._emit(BOX, *P(0, yb), th, 0, W, .4, T['yard_wall_m'], part=part, g_m=g)
                self._emit(BOX, *P(-W / 2 + .2, (y0_ + yb) / 2), th, 0, .4, yb - y0_ - .4, T['yard_wall_m'], part=part, g_m=g); self.found = 0.0
        elif f == 'court':
            k = math.sqrt(T['court']['frac']); rx, ry = max(4.0, W * (1 - k) / 2), max(4.0, D * (1 - k) / 2)
            if W - 2 * rx < 3 or D - 2 * ry < 3: raise SystemExit(f'citygen: a court house on a {lw:g} x {ld:g} m lot: no room for its court (each wing is 4 m deep at least); give its fabric a larger lot')
            cy = -ld / 2 + front + D / 2; g = self.gsite(*P(0, cy - pm / 2), th, W, D + pm)   # (one building: one level)
            self.house_body(*P(0, cy - D / 2 + ry / 2), th, W, ry, n, T, part, gate=True, g=g)                  # the street wing
            self.house_body(*P(0, cy + D / 2 - ry / 2), th, W, ry, n, T, part, street=False, g=g)               # the back wing
            for s_ in (-1, 1):                                                                                 # the side wings
                self.house_body(*P(s_ * (W / 2 - rx / 2), cy), th + math.pi / 2, D - 2 * ry, rx, n, T, part, street=False, g=g)
            self.found = 0.0
        else:   # compound: inside its wall
            W, D = W - 1.0, D - 1.0; k = math.sqrt(T['court']['frac']); cy = -ld / 2 + front + .5 + D / 2
            md = min(12.0, max(4.0, D * (1 - k) * .6)); fd = min(8.0, D * (1 - k) * .4); sd = min(8.0, max(3.5, W * (1 - k) / 2))
            n2 = max(T['storeys'][0], n - 1); gap = .8; fz = fd if fd >= 3.5 else 2.4
            self.house_body(*P(0, cy + D / 2 - md / 2), th, W * .9, md, n, T, part)                                # the main building
            sl = D - md - fz - 2 * gap
            if sl > 3:
                for s_ in (-1, 1): self.house_body(*P(s_ * (W / 2 - sd / 2), cy - D / 2 + fz + gap + sl / 2), th + math.pi / 2, sl, sd, n2, T, part, street=False)
            if fd >= 3.5: self.house_body(*P(0, cy - D / 2 + fd / 2), th, W * .7, fd, n2, T, part, gate=True)       # the front building, the gate through it
            elif self.det >= 1:   # a gate house in the wall
                gx, gy = P(0, cy - D / 2 + 1.2); g = self.gsite(gx, gy, th, 4, 2.4)
                self._emit(BOX, gx, gy, th, 0, 4, 2.4, 3.0, part=part, g_m=g); self.house_roof(gx, gy, th, 3.0, 4, 2.4, R, True, g)
                self._emit(BOX, *P(0, cy - D / 2 - .05), th, .1, 1.5, .2, 2.3, part=DARK, g_m=g); self.found = 0.0
            if T['yard_wall_m'] and self.det >= 1: self._yard_wall(P, lw, ld, m, T['yard_wall_m'], part)

    def _yard_wall(self, P, lw, ld, m, h, part):
        """the wall round a lot (P: the lot's frame) just inside its margin, a gate gap in the middle of its street side"""
        e = m + .2; a, b, c, d = P(-lw / 2 + e, -ld / 2 + e), P(lw / 2 - e, -ld / 2 + e), P(lw / 2 - e, ld / 2 - e), P(-lw / 2 + e, ld / 2 - e)
        for p, q in ((b, c), (c, d), (d, a), (a, P(-1.6, -ld / 2 + e)), (P(1.6, -ld / 2 + e), b)): self.strip(p, q, .4, h, part=part)

    def house_body(self, x, y, th, w, d, n, T, part=FAB, street=True, gate=False, along=True, ends=True, g=None):
        """one building of a declared type on a w x d footprint (a portico, when the type has one, before it on the street side,
        local -y): n storeys of T's storey_m, on a podium a little smaller than the footprint when the type has one (its stair in
        front); on the street side the ground storey is closed with a door, open shop fronts (shops), or set back behind posts
        under the storeys above (arcade), a row of windows on every storey (detail high); gate: a passage through it instead of
        a door; then the type's roof (house_roof). g: the ground it stands on (one level for the wings of one building), else
        its own (gsite)"""
        P = self.frame(x, y, th); sm = T['storey_m']; hb = n * sm; pm = T['portico_m'] if street else 0; pz = T['podium_m']
        grd = T['ground'] if street else 'closed'; own = g is None
        if own: g = self.gsite(*P(0, -pm / 2), th, w, d + pm)
        z = 0.0
        if pz:   # the podium under the body and the portico, the stair before it; the body .6 m in from its edges
            self._emit(BOX, *P(0, -pm / 2), th, 0, w, d + pm, pz, part=part, g_m=g)
            if street: self.stair(P, 0, -d / 2 - pm, th, min(6.0, w * .4), pz, pz * 1.4, g, part=part)
            z = pz; w, d = w - 1.2, d - 1.2
        if grd == 'arcade':   # the ground storey behind the walk, posts on the front line, the storeys above over the walk
            a = T['arcade_m']; self._emit(BOX, *P(0, a / 2), th, z, w, d - a, sm, part=part, g_m=g)
            k_ = max(2, round(w / 3.6))
            for i in range(k_ + 1): self._emit(BOX, *P(-w / 2 + .3 + (w - .6) * i / k_, -d / 2 + .3), th, z, .6, .6, sm, part=part, g_m=g)
            self._emit(BOX, x, y, th, z + sm, w, d, hb - sm, part=part, g_m=g)
            if self.det >= 1: self._emit(BOX, *P(0, -d / 2 + a - .05), th, z + .1, w * .8, .2, sm * .72, part=DARK, g_m=g)
        else:
            self._emit(BOX, x, y, th, z, w, d, hb, part=part, g_m=g)
            if self.det >= 1 and street:
                if gate: self._emit(BOX, x, y, th, z, 2.6, d + .2, min(3.4, sm * .9), part=DARK, g_m=g)   # the passage through
                elif grd == 'shops': self.shopfront(*P(0, -d / 2 - .05), th, z, w * .82, min(2.8, sm * .78), part, g)
                else: self._emit(BOX, *P(0, -d / 2 - .05), th, z + .1, min(1.4, w * .3), .2, min(2.3, sm * .72), part=DARK, g_m=g)
        if self.det >= 2 and street:   # windows, every storey, on the street side
            k_ = max(1, min(6, int(w // 3.6)))
            for s_ in range(0 if grd == 'closed' else 1, n):
                for i in range(k_):
                    lx = -w / 2 + w * (i + .5) / k_
                    if s_ == 0 and abs(lx) < 1.8: continue   # (the door, the passage)
                    self._emit(BOX, *P(lx, -d / 2 - .05), th, z + s_ * sm + sm * .38, min(1.0, w / k_ * .4), .2, min(1.5, sm * .42), part=DARK, g_m=g)
        if pm:   # the portico: posts along its front, a lean-to roof from the wall
            k_ = max(2, round(w / 3.2))
            for i in range(k_ + 1): self._emit(BOX, *P(-w / 2 + .3 + (w - .6) * i / k_, -d / 2 - pm + .3), th, z, .5, .5, sm, part=part, g_m=g)
            self.lean(*P(0, -d / 2 - pm / 2), th, w, pm + .6, z + sm + .7, .7, part=ROOF, g=g)
        self.house_roof(x, y, th, z + hb, w, d, T['roof'], along, g, ends)
        if own: self.found = 0.0

    def house_roof(self, x, y, th, z0, w, d, R, along=True, g=None, ends=True):
        """a declared type's roof over a w x d body whose eaves are at z0 (R: shape, pitch_deg, overhang_m; ROOF_SHAPES), its
        ridge along local x (w), or along local y when not along; a hipped roof's ridge runs along the longer side. ends False:
        no eaves past the ends of a ridge along w (the party walls of a row)"""
        if not along: th, w, d = th + math.pi / 2, d, w
        s, o, tn = R['shape'], R['overhang_m'], math.tan(math.radians(R['pitch_deg'])); W, D = w + 2 * o, d + 2 * o
        L = W if ends or not along else w
        if s == 'flat':   # a slab, a parapet round it when it has no eaves
            self._emit(BOX, x, y, th, z0, L, D, .35, part=ROOF, g_m=g)
            if self.det >= 1 and o < .2:
                P = self.frame(x, y, th)
                for lx, ly, a, b in ((0, -D / 2 + .15, L, .3), (0, D / 2 - .15, L, .3), (-L / 2 + .15, 0, .3, D - .6), (L / 2 - .15, 0, .3, D - .6)):
                    self._emit(BOX, *P(lx, ly), th, z0 + .35, a, b, .8, part=FAB, g_m=g)
        elif s == 'gabled':
            L = w + 2 * o * .6 if ends or not along else w; rh = d / 2 * tn
            self._emit(GABLE, x, y, th + math.pi / 2, z0, d, L, rh, o, part=ROOF, g_m=g)
            if self.det >= 1: self._emit(BOX, x, y, th, z0 + rh - .2, L + (.2 if ends or not along else 0), .35, .45, part=ROOF, g_m=g)   # the ridge
        elif s in ('hipped', 'pyramidal'):
            rh = min(W, D) / 2 * tn
            top = (.02, .02) if s == 'pyramidal' else (max(W - D, .02), .02) if W >= D else (.02, max(D - W, .02))
            self._emit(FRUSTUM, x, y, th, z0, W, D, rh, *top, part=ROOF, g_m=g)
        elif s == 'skillion':   # one slope falling to local -y: the walls rise to it (a sheared box, its lower part inside the body), a slab on top
            rh = d * tn; k = tn * self.hex / self.gex; s0 = self.slope; self.slope = (-math.sin(th) * k, math.cos(th) * k)
            self._emit(BOX, x, y, th, z0 - rh / 2 - .1, w - .06, d - .1, rh + .1, part=FAB, g_m=g); self.slope = s0
            self.lean(x, y, th, L, D, z0 + rh / 2 + tn * D / 2 + .3, tn * D, part=ROOF, g=g, t=.3)
        elif s == 'mansard':   # a steep lower slope (pitch_deg) all round, about a storey high, a low hipped top
            h1 = min(3.2, .35 * min(w, d)); a = h1 / tn; Wt, Dt = W - 2 * a, D - 2 * a; rh = min(Wt, Dt) / 2 * math.tan(math.radians(15))
            self._emit(FRUSTUM, x, y, th, z0, W, D, h1, Wt, Dt, part=ROOF, g_m=g)
            self._emit(FRUSTUM, x, y, th, z0 + h1, Wt, Dt, rh, *((max(Wt - Dt, .02), .02) if Wt >= Dt else (.02, max(Dt - Wt, .02))), part=ROOF, g_m=g)
        elif s == 'gambrel':   # a steep lower slope (pitch_deg) on the two long sides, a gentle gable above
            h1 = min(3.2, .35 * d); a = h1 / tn; dt = D - 2 * a
            self._emit(FRUSTUM, x, y, th, z0, L, D, h1, L, dt, part=ROOF, g_m=g)
            self._emit(GABLE, x, y, th + math.pi / 2, z0 + h1, dt, L, dt / 2 * math.tan(math.radians(25)), 0, part=ROOF, g_m=g)

    # ------------------------------------------------------------------ walls
    def walls(self, ring, h=10.0, t=10.0, gates=(), towers=True, part=WALL, gate_style='tower', moat=None, bastion_m=80.0, moat_w=16.0, moat_off=None):
        """a city wall along a closed ring (UTM points): battered rammed-earth body, merlons on the outer parapet, bastions
        (马面), corner towers, gate towers over dark passages, barbicans (瓮城) and a moat with bridges"""
        poly = orient(Polygon(ring), 1.0)            # counter-clockwise: the outside is to the right of the direction
        ring = list(poly.exterior.coords)
        line = LineString(ring); L = line.length
        gl = sorted([(line.project(Point(g_[0], g_[1])), (g_[2] if len(g_) > 2 else 4.0)) for g_ in gates])   # (position, pier width)
        gpos = [gp for gp, _ in gl]
        gw = 16.0
        if gate_style == 'han3':   # 一门三道 (han_changan.md §2-B): three 8 m passages, piers 4 m (14 m facing a palace), 20 m deep
            cuts = [(gp - (24 + 2 * pw) / 2, gp + (24 + 2 * pw) / 2) for gp, pw in gl]
        else: cuts = [(gp - gw / 2, gp + gw / 2) for gp in gpos]
        verts = [0.0]
        for i in range(1, len(ring)): verts.append(verts[-1] + math.hypot(ring[i][0] - ring[i - 1][0], ring[i][1] - ring[i - 1][1]))
        def pieces(s0, s1, most=60.0):   # wall pieces between corners and gates, at most `most` metres: each sits on its own ground
            out = []; bnd = [s0] + [v for v in verts if s0 < v < s1] + [s1]
            for a_, b_ in zip(bnd[:-1], bnd[1:]):
                if b_ - a_ <= .5: continue
                n = max(1, math.ceil((b_ - a_) / most))
                for k in range(n): out.append((line.interpolate(a_ + (b_ - a_) * k / n), line.interpolate(a_ + (b_ - a_) * (k + 1) / n)))
            return out
        spans = []; prev = 0.0
        for c0, c1 in cuts: spans.append((prev, max(prev, c0))); prev = c1
        spans.append((prev, L))
        tower = gate_style == 'tower'
        npc = 0   # wall pieces so far: a bastion (马面) on every other piece's middle
        for s0, s1 in spans:
            for pa, pb in pieces(s0, s1, most=min(60.0, bastion_m * .75)):
                npc += 1; self.group()
                th = math.atan2(pb.y - pa.y, pb.x - pa.x); mx, my = (pa.x + pb.x) / 2, (pa.y + pb.y) / 2; ln = math.hypot(pb.x - pa.x, pb.y - pa.y)
                g, self.slope, self.found = self.lay((pa.x, pa.y), (pb.x, pb.y), t)   # the wall runs along the slope, no steps
                ox_, oy_ = math.sin(th), -math.cos(th)                       # outward normal (right of the direction)
                self._emit(FRUSTUM, mx, my, th, 0, ln + t * .2, t, h, ln + t * .1, t * .66, part=part, g_m=g)
                if tower:
                    po = t * .66 / 2 - .4
                    self._emit(BOX, mx - ox_ * po, my - oy_ * po, th, h, ln, .5, 1.0, part=part, g_m=g)                  # inner parapet
                    if self.det >= 1:
                        self._emit(BOX, mx + ox_ * po, my + oy_ * po, th, h, ln, .8, .9, part=part, g_m=g)              # outer parapet
                        n = int(ln // 2.8)
                        for i in range(n):                                                                               # merlons
                            k = (i + .5) / n; px, py = pa.x + (pb.x - pa.x) * k + ox_ * po, pa.y + (pb.y - pa.y) * k + oy_ * po
                            self._emit(BOX, px, py, th, h + .9, 1.4, .8, 1.0, part=part, g_m=g + self.slope[0] * (px - mx) + self.slope[1] * (py - my))
                self.slope = None; self.found = 0.0
                if tower and self.det >= 1 and npc % 2 == 0 and ln > 20:                                                # bastions, each on its own ground
                    bx_, by_ = mx + ox_ * (t * .5 + 3.5), my + oy_ * (t * .5 + 3.5)
                    gb_ = self.gsite(bx_, by_, th, 13, 9); self._emit(FRUSTUM, bx_, by_, th, 0, 13, 9, h, 12, 7.5, part=part, g_m=gb_); self.found = 0.0
        if towers:   # corner towers (角楼)
            for i in range(len(ring) - 1):
                x, y = ring[i]; self.group(); g = self.gsite(x, y, 0, t * 1.9, t * 1.9)
                self._emit(BOX, x, y, 0, 0, t * 1.9, t * 1.9, h * 1.04, part=part, g_m=g)
                if tower and self.det >= 1: self.hall(x, y, math.pi / 4, t * 1.1, t * 1.1, h * .9, roof='xieshan', z0=h * 1.04, part=LMK, g=g, cols=False)
                else: self._emit(FRUSTUM, x, y, 0, h * 1.04, t * 1.7, t * 1.7, h * .35, t * .6, t * .6, part=LROOF, g_m=g)
        for gp, pw in (gl if gate_style == 'han3' else []):   # a Han gate: its platform over three passages, a tower on top
            p = line.interpolate(gp); q = line.interpolate(min(L, gp + 1.0)); th = math.atan2(q.y - p.y, q.x - p.x)
            W = 24 + 2 * pw + 8; D = max(20.0, t + 4); self.group(); g = self.gsite(p.x, p.y, th, W, D); self.found = 0.0
            self._emit(BOX, p.x, p.y, th, 0, W, D, h, part=part, g_m=g)
            for k in (-1, 0, 1):
                qx, qy = p.x + math.cos(th) * k * (8 + pw), p.y + math.sin(th) * k * (8 + pw); self._emit(BOX, qx, qy, th, 0, 7.6, D + .4, min(7.5, h * .62), part=DARK, g_m=g)
            self.hall(p.x, p.y, th, W * .86, D * .7, 11, roof='double_hip' if pw > 8 else 'hip', z0=h, part=LMK, g=g, front=1)
        for gp in (gpos if gate_style not in ('none', 'han3') else []):   # gate towers (城楼) over the passages, barbicans outward
            p = line.interpolate(gp); q = line.interpolate(min(L, gp + 1.0)); th = math.atan2(q.y - p.y, q.x - p.x)
            self.group(); g = self.gsite(p.x, p.y, th, gw * 2.2, t * 1.3); ox_, oy_ = math.sin(th), -math.cos(th)
            self._emit(BOX, p.x, p.y, th, 0, gw * 2.2, t * 1.3, h, part=part, g_m=g)
            self._emit(BOX, p.x, p.y, th, 0, 5.5, t * 1.3 + .4, min(7, h * .7), part=DARK, g_m=g)                   # the passage
            self.hall(p.x, p.y, th, gw * 1.8, t * .9, h * 1.25, roof='double' if tower else 'xieshan', z0=h, part=LMK, g=g, front=1)
            if tower:
                for k in (-1, 1):
                    ex, ey = p.x + math.cos(th) * k * gw * 1.6 + ox_ * t * 2.2, p.y + math.sin(th) * k * gw * 1.6 + oy_ * t * 2.2
                    self._emit(BOX, ex, ey, th + math.pi / 2, 0, t * 3.2, t * .7, h * .9, part=part, g_m=g)
                fx, fy = p.x + ox_ * t * 3.8, p.y + oy_ * t * 3.8
                self._emit(BOX, fx, fy, th, 0, gw * 3.4, t * .7, h * .9, part=part, g_m=g)
                if self.det >= 1:   # the barbican's own gate (offset sideways, as usual) and its arrow tower
                    sx, sy = fx + math.cos(th) * gw * .9, fy + math.sin(th) * gw * .9
                    self._emit(BOX, sx, sy, th, 0, 5, t * .7 + .4, min(6, h * .6), part=DARK, g_m=g)
                    self.hall(fx, fy, th, gw * 1.6, t * .6, h * .8, roof='xieshan', z0=h * .9, part=LMK, g=g, cols=False, front=1)
        if (moat if moat is not None else tower):   # a moat ring outside, with a bridge at each gate
            d0 = t * .5 + moat_off + moat_w / 2 if moat_off is not None else t * .5 + (t * 3.8 + 14 if tower else 18)
            mo = poly.buffer(d0, join_style=2)
            mring = list(mo.exterior.coords)
            for a, b in zip(mring[:-1], mring[1:]):
                self.strip(a, b, moat_w, .25, part=WATER)
            for gp in gpos:
                p = line.interpolate(gp); q = line.interpolate(min(L, gp + 1.0)); th = math.atan2(q.y - p.y, q.x - p.x)
                ox_, oy_ = math.sin(th), -math.cos(th)
                if tower: p = Point(p.x + math.cos(th) * gw * .9, p.y + math.sin(th) * gw * .9)
                a = (p.x + ox_ * (d0 - moat_w / 2 - 6), p.y + oy_ * (d0 - moat_w / 2 - 6)); b = (p.x + ox_ * (d0 + moat_w / 2 + 6), p.y + oy_ * (d0 + moat_w / 2 + 6))
                self.strip(a, b, 7, .9, part=BRIDGE)

    # ------------------------------------------------------------------ fabric
    def fill(self, region, theta, lot=(18.0, 26.0), typ='courtyard', h=6.0, empty=.06, part=FAB, jitter=.08, avoid=None, scatter=0.0):
        """subdivide a region (shapely polygon, UTM) into an oriented grid of lots and put a house in each lot"""
        if region.is_empty: return 0
        if avoid is not None and not avoid.is_empty: region = region.difference(avoid)
        if region.is_empty or region.area < lot[0] * lot[1]: return 0
        cx, cy = region.centroid.x, region.centroid.y
        R = affinity.rotate(region, -theta, origin=(cx, cy), use_radians=True)
        x0, y0, x1, y1 = R.bounds; lw, ld = lot
        xs = np.arange(x0, x1, lw); ys = np.arange(y0, y1, ld)
        if len(xs) * len(ys) == 0: return 0
        X, Y = np.meshgrid(xs, ys); X = X.ravel(); Y = Y.ravel()
        cells = shapely.box(X, Y, X + lw, Y + ld)
        frac = shapely.area(shapely.intersection(cells, R)) / (lw * ld)
        keep = np.nonzero(frac > .985)[0]   # whole lots only: no house straddles a lane or a street
        c, s = math.cos(theta), math.sin(theta); n = 0
        for i in keep:
            if self.rng.random() < empty: continue
            self.group()
            lx, ly = X[i] + lw / 2 - cx, Y[i] + ld / 2 - cy
            if scatter: lx += (self.rng.random() - .5) * lw * scatter * .6; ly += (self.rng.random() - .5) * ld * scatter * .6
            px, py = cx + lx * c - ly * s, cy + lx * s + ly * c
            if scatter: theta_i = theta + (self.rng.random() - .5) * .7 * scatter
            else: theta_i = theta
            j = self.rng.random
            w_, d_ = lw * (1 - jitter * j()), ld * (1 - jitter * j())
            with self.lot_site(px, py, theta_i, lw, ld): self._lot(typ, px, py, theta_i, lw, ld, w_, d_, h, part, j)
            n += 1
        return n

    def _lot(self, typ, px, py, theta_i, lw, ld, w_, d_, h, part, j):
        """one lot of a fabric (fill): its house, on the lot made one plane (lot_site)"""
        if typ == 'courtyard': self.courtyard(px, py, theta_i, w_ * .96, d_ * .96, h * (.85 + .3 * j()), part=part)
        elif typ == 'dwelling':   # one or two small gable wings in a walled yard (commoners' houses, workshops)
            self.gable_house(px, py + d_ * .18, theta_i, w_ * .8, d_ * .4, h * (.8 + .4 * j()), part=part, front=-1)
            if j() < .55: self.gable_house(px - w_ * .28, py - d_ * .18, theta_i + math.pi / 2, d_ * .3, w_ * .3, h * .75, part=part, front=-1)
            if self.det >= 1:
                P = self.frame(px, py, theta_i)
                for (a, b) in ((P(-w_ / 2, -d_ / 2), P(w_ * .1, -d_ / 2)), (P(w_ * .3, -d_ / 2), P(w_ / 2, -d_ / 2)), (P(w_ / 2, -d_ / 2), P(w_ / 2, d_ / 2)), (P(-w_ / 2, -d_ / 2), P(-w_ / 2, d_ / 2))):
                    self.strip(a, b, .4, 2.0, part=part)
        elif typ == 'hut': self.hut(px, py, min(lw, ld) * .32, h, part=part)
        elif typ == 'slab': self.slab(px, py, theta_i, w_ * .8, d_ * .35, h, part=part)
        else: self.house(px, py, theta_i, lw, ld, self.types[typ], part=part)   # a declared type (house_types)


def to_utm_ring(F, ring):
    return [F.to_utm.transform(lon, lat) for lon, lat in ring]


def traced(spec, F, city_dir):
    """a period city drawn over an old map or a site plan: spec `trace` names GeoJSON files (one or a list) under the city's
    folder, in lon/lat, traced over the map once it is georeferenced (QGIS's georeferencer, then its drawing tools; or geojson.io
    over a map laid in place). Each feature's properties.kind says what it becomes; its other properties are that entry's keys:
      wall      Polygon        walls      {ring, h_m, t_m, gates, towers, style, moat}
      street    LineString     streets    {pts, w_m, shops}
      block     Polygon        fabric     {region, lot, typ, h_m, empty}; theta_deg defaults to the block's long side, so the lots
                                          run with the block as drawn, not with the city's grid
      landmark  Point/Polygon  landmarks  {kind: properties.type, lon, lat, ...}; a polygon gives its centre, w_m (the long side),
                                          d_m and theta_deg, which properties written on the feature override
    Returns {walls, streets, fabric, landmarks}: lists to add to the spec's own (written entries and traced ones build alike)."""
    import json, os
    paths = spec.get('trace') or []
    out = {'walls': [], 'streets': [], 'fabric': [], 'landmarks': []}
    for path in ([paths] if isinstance(paths, str) else paths):
        for f in json.load(open(os.path.join(city_dir, path), encoding='utf-8')).get('features', []):
            pr = dict(f.get('properties') or {}); kind = pr.pop('kind', None); g = f.get('geometry') or {}; t, c = g.get('type'), g.get('coordinates')
            ring = None
            if t == 'Polygon':
                ring = [list(q[:2]) for q in c[0]]
                if len(ring) > 3 and ring[0] == ring[-1]: ring = ring[:-1]   # (GeoJSON closes its rings; the spec's do not repeat the first point)
                r_ = shapely.minimum_rotated_rectangle(Polygon(to_utm_ring(F, ring)))
                q_ = list(r_.exterior.coords); e1, e2 = (q_[1][0] - q_[0][0], q_[1][1] - q_[0][1]), (q_[2][0] - q_[1][0], q_[2][1] - q_[1][1])
                lo, sh = (e1, e2) if math.hypot(*e1) >= math.hypot(*e2) else (e2, e1)
                long_deg = math.degrees(math.atan2(lo[1], lo[0])) % 180
            if kind == 'wall' and t == 'Polygon': out['walls'].append({'ring': ring, **pr})
            elif kind == 'street' and t == 'LineString': out['streets'].append({'pts': [list(q[:2]) for q in c], **pr})
            elif kind == 'block' and t == 'Polygon': out['fabric'].append({'region': ring, 'theta_deg': round(long_deg, 2), **pr})
            elif kind == 'landmark' and t == 'Point': out['landmarks'].append({'kind': pr.pop('type', 'hall'), 'lon': c[0], 'lat': c[1], **pr})
            elif kind == 'landmark' and t == 'Polygon':
                cx, cy = F.to_wgs.transform(*r_.centroid.coords[0])
                out['landmarks'].append({'kind': pr.pop('type', 'hall'), 'lon': round(cx, 6), 'lat': round(cy, 6), 'w_m': round(math.hypot(*lo), 1),
                                         'd_m': round(math.hypot(*sh), 1), 'theta_deg': round(long_deg, 2), **pr})
            else: raise SystemExit(f'citygen: {path}: a feature of kind {kind!r} on a {t}: wall (Polygon), street (LineString), block (Polygon), landmark (Point or Polygon)')
    return out


def with_trace(spec, F, city_dir):
    """the spec with its traced features (traced) joined to its own lists"""
    if not spec.get('trace'): return spec
    return {**spec, **{k: list(spec.get(k, [])) + v for k, v in traced(spec, F, city_dir).items() if v}}


BUILTIN_TYPES = ('courtyard', 'dwelling', 'hut', 'slab', 'wards')   # the generator's own houses: one region's (north China)
TYPES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'types')   # the shared library of house types
FORMS = ('detached', 'row', 'court', 'compound')
ROOF_SHAPES = {'flat': 0, 'gabled': 30, 'hipped': 25, 'pyramidal': 25, 'skillion': 12, 'mansard': 70, 'gambrel': 60}   # OpenStreetMap roof:shape -> its usual pitch (mansard, gambrel: the steep lower slope)
ROOF_LATER = ('dome', 'onion', 'round')   # (they need a round primitive the engine does not have yet)
TYPE_KEYS = ('where', 'when', 'basis', 'form', 'storeys', 'storey_m', 'roof', 'court', 'yard_wall_m', 'ground', 'arcade_m', 'portico_m', 'podium_m')


def house_type(T, src):
    """a house type checked and completed with its defaults (docs/MODEL.md "House types"). Each key is a fact from the sources
    about the houses of one place and time, and where, when and basis say which: a type without them, a key it does not have,
    a key its form does not use or a value out of range stops compile with what to write (src: where the type is written).
    The result holds the keys its form uses, so it passes again unchanged"""
    def no(m): raise SystemExit(f'citygen: {src}: {m}')
    def num(k, v, lo, hi):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not lo <= v <= hi: no(f'{k}: {v!r}: a number from {lo:g} to {hi:g}')
        return float(v)
    if not isinstance(T, dict): no('a house type is a mapping of its keys (docs/MODEL.md "House types")')
    bad = sorted(set(T) - set(TYPE_KEYS))
    if bad: no(f'no key {", ".join(bad)} (a house type has {", ".join(TYPE_KEYS)})')
    for k in ('where', 'when', 'basis'):
        if not str(T.get(k) or '').strip(): no(f'{k} is missing: a house type says where its houses stood, when, and on what basis (the research it comes from)')
    f = T.get('form')
    if f not in FORMS: no(f'form: {f!r}: one of {", ".join(FORMS)}')
    st = T.get('storeys'); st = [st, st] if isinstance(st, int) and not isinstance(st, bool) else st
    if not (isinstance(st, list) and len(st) == 2 and all(isinstance(v, int) and not isinstance(v, bool) for v in st) and 1 <= st[0] <= st[1] <= 40):
        no(f'storeys: {T.get("storeys")!r}: [fewest, most] whole storeys from 1 to 40, or one number when all have as many')
    R = T.get('roof')
    if not isinstance(R, dict) or 'shape' not in R: no('roof: { shape, pitch_deg, overhang_m, ridge }, shape at least')
    bad = sorted(set(R) - {'shape', 'pitch_deg', 'overhang_m', 'ridge'})
    if bad: no(f'roof: no key {", ".join(bad)} (shape, pitch_deg, overhang_m, ridge)')
    s = R['shape']
    if s in ROOF_LATER: no(f'roof.shape {s}: not drawn yet (it needs a round primitive the engine does not have yet)')
    if s not in ROOF_SHAPES: no(f'roof.shape {s!r}: one of {", ".join(ROOF_SHAPES)} (OpenStreetMap roof:shape)')
    pitch = num('roof.pitch_deg', R.get('pitch_deg', ROOF_SHAPES[s]), 0, 80)
    if s == 'flat' and pitch: no('roof.pitch_deg: a flat roof has no pitch')
    if s in ('mansard', 'gambrel') and not 45 <= pitch <= 80: no(f'roof.pitch_deg {pitch:g}: a {s} roof gives its steep lower slope, 45 to 80')
    if s not in ('flat', 'mansard', 'gambrel') and not 5 <= pitch <= 60: no(f'roof.pitch_deg {pitch:g}: 5 to 60 for a {s} roof')
    roof = {'shape': s, 'pitch_deg': pitch, 'overhang_m': num('roof.overhang_m', R.get('overhang_m', 0 if s == 'flat' else .5), 0, 3)}
    if f in ('detached', 'row'):
        roof['ridge'] = R.get('ridge', 'along')
        if roof['ridge'] not in ('along', 'across'): no(f'roof.ridge: {roof["ridge"]!r}: along (the ridge along the street) or across (the gable to the street)')
    elif 'ridge' in R: no(f'roof.ridge: a {f} house runs each ridge along its wing; only a detached or a row house turns it')
    out = {'where': str(T['where']), 'when': str(T['when']), 'basis': str(T['basis']), 'form': f, 'storeys': list(st),
           'storey_m': num('storey_m', T.get('storey_m', 3.2), 2.2, 8), 'roof': roof}
    if f in ('court', 'compound'):
        C_ = T.get('court', {})
        if not isinstance(C_, dict) or set(C_) - {'frac'}: no('court: { frac } (the court\'s share of the lot, .05 to .7)')
        out['court'] = {'frac': num('court.frac', C_.get('frac', .3), .05, .7)}
    elif 'court' in T: no(f'court: a {f} house has no court (form court or compound)')
    if f == 'court' and 'yard_wall_m' in T: no('yard_wall_m: a court house is its own wall')
    if f != 'court': out['yard_wall_m'] = num('yard_wall_m', T.get('yard_wall_m', 2.4 if f == 'compound' else 0), 0, 8)
    out['ground'] = T.get('ground', 'closed')
    if out['ground'] not in ('closed', 'shops', 'arcade'): no(f'ground: {out["ground"]!r}: closed, shops (open shop fronts on the street) or arcade (posts under the upper storeys)')
    if out['ground'] == 'arcade':
        if st[0] < 2: no('ground: arcade stands the upper storeys over the walk, so storeys from 2 (a one-storey house with a covered walk before it writes portico_m)')
        if T.get('portico_m'): no('ground: arcade and portico_m: one walk or the other')
        out['arcade_m'] = num('arcade_m', T.get('arcade_m', 3.0), 1.5, 8)
    elif 'arcade_m' in T: no('arcade_m: only with ground: arcade')
    out['portico_m'] = num('portico_m', T.get('portico_m', 0), 0, 8); out['podium_m'] = num('podium_m', T.get('podium_m', 0), 0, 6)
    return out


def house_types(spec, shared=None, label='city'):
    """the house types a period city can build, name -> complete type (house_type): each it declares (city.types) or the city
    declares for all its periods (city.yaml types), and each its fabric names, looked up in that order and then in the shared
    library, types/<name>.yaml. A type written in the city may start `from:` another (declared or in the library) and change
    some keys; it still says its own where, when and basis. A fabric typ neither built in nor found, or the fabric of a
    declared type giving h_m (its height is its storeys), stops compile. Call it after with_trace: traced blocks name types."""
    own, common = spec.get('types') or {}, shared or {}
    for src, d in ((f'{label}: city.types', own), ('city.yaml: types', common)):
        if not isinstance(d, dict): raise SystemExit(f'citygen: {src}: a mapping, type name -> type')
    out = {}
    def get(name, via=()):
        if name in out: return out[name]
        if name in BUILTIN_TYPES: raise SystemExit(f'citygen: {label}: house type {name!r} is a built-in name ({", ".join(BUILTIN_TYPES)}): give the type a name of its own')
        if name in via: raise SystemExit(f'citygen: {label}: house types {" -> ".join(via + (name,))}: a type made from itself; give it a name of its own')
        if name in own: T, src = own[name], f'{label}: city.types.{name}'
        elif name in common: T, src = common[name], f'city.yaml: types.{name}'
        else:
            p = os.path.join(TYPES_DIR, f'{name}.yaml')
            if not os.path.isfile(p): raise SystemExit(f'citygen: {label}: house type {name!r} is not built in ({", ".join(BUILTIN_TYPES)}), not declared (city.types, city.yaml types) and not in the shared library (types/{name}.yaml)')
            import yaml
            T, src = yaml.safe_load(open(p, encoding='utf-8')), f'types/{name}.yaml'
            if isinstance(T, dict) and 'from' in T: raise SystemExit(f'citygen: {src}: from: a library type is written out whole')
        if isinstance(T, dict) and 'from' in T:   # the base's keys, then this type's (roof and court key by key); keys the new form does not use go
            miss = [k for k in ('where', 'when', 'basis') if not str(T.get(k) or '').strip()]
            if miss: raise SystemExit(f'citygen: {src}: {", ".join(miss)} missing: a type made from another says its own where, when and basis (what it changes, and from which sources)')
            b = get(T['from'], via + (name,)); f = T.get('form', b['form']); g_ = T.get('ground', b['ground'])
            drop = {k for k, out_ in (('court', f not in ('court', 'compound')), ('yard_wall_m', f == 'court'), ('arcade_m', g_ != 'arcade')) if out_}
            M = {k: v for k, v in b.items() if k not in drop}; M.update({k: v for k, v in T.items() if k != 'from'})
            for k in ('roof', 'court'):
                if isinstance(b.get(k), dict) and isinstance(T.get(k), dict): M[k] = {**b[k], **T[k]}
            if f not in ('detached', 'row') and 'ridge' not in (T.get('roof') or {}): M['roof'] = {k: v for k, v in M['roof'].items() if k != 'ridge'}
            if 'shape' in (T.get('roof') or {}) and 'pitch_deg' not in T['roof']: M['roof'].pop('pitch_deg', None)   # (a new shape: its own usual pitch)
            T = M
        out[name] = house_type(T, src); return out[name]
    for name in list(own) + list(common): get(name)   # every declared type is checked, built or not
    for fb in spec.get('fabric', []):
        typ = fb.get('typ', 'courtyard')
        if typ in BUILTIN_TYPES: continue
        get(typ)
        if 'h_m' in fb: raise SystemExit(f'citygen: {label}: a fabric of type {typ} gives h_m: a declared type is as tall as its storeys (storeys x storey_m); drop h_m')
    return out


def _lines(geom):
    if geom.is_empty: return []
    if isinstance(geom, LineString): return [geom]
    return [g for g in getattr(geom, 'geoms', []) if isinstance(g, LineString)]


def extent(spec, F, osm_rings=None):
    """where a period city builds (UTM): its walls' rings, its fabric regions, its landmarks' rectangles (30 m round a point
    without a size), its streets (terrain.py measures the ground there)"""
    parts = [Polygon(to_utm_ring(F, w['ring']) if 'ring' in w else to_utm_ring(F, osm_rings(w['osm'])[0])) for w in spec.get('walls', [])]
    for fb in spec.get('fabric', []):
        r = fb.get('region', 'walls')
        if r != 'walls': parts.append(Polygon(to_utm_ring(F, osm_rings(r[4:])[0]) if isinstance(r, str) else to_utm_ring(F, r)))
    for L in spec.get('landmarks', []):
        if 'lon' not in L: continue
        x, y = F.to_utm.transform(L['lon'], L['lat']); th = math.radians(L.get('theta_deg', spec.get('theta_deg', 0))); c_, s_ = math.cos(th), math.sin(th)
        hw, hd = L.get('w_m', 60) / 2, L.get('d_m', L.get('w_m', 60)) / 2
        parts.append(Polygon([(x + u * c_ - v * s_, y + u * s_ + v * c_) for u, v in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd))]))
    parts += [LineString([F.to_utm.transform(*q) for q in st['pts']]).buffer(st.get('w_m', 14) / 2) for st in spec.get('streets', [])]
    return unary_union(parts) if parts else Polygon()

def build_city(spec, F, ground_m, exag, osm_rings=None, extra_avoid=None, meta=None):
    """spec (dict from city.yaml, lon/lat) -> primitive list. Spec keys:
    origin [lon, lat]; theta_deg (grid rotation, CCW from east); detail (low | medium | high); exaggeration (building heights,
    default 2: close shots keep the proportions; the ground uses the plate's `exag`);
    trace: GeoJSON drawn over an old map or a site plan (traced; the callers join it: compile, terrain.py);
    walls: [{ring|osm, h_m, t_m, gates: [[lon,lat],...], towers, style: tower|hip|none, moat}];
    streets: [{pts, w_m, shops}]; lanes: {spacing_m, w_m, theta_deg, region}; fabric: [{region: ring|'walls', lot: [w,d], typ, h_m, empty}]
    (typ: a built-in house or one of `types`, complete: house_types);
    landmarks: [{kind, lon, lat, ...}]; trees: [{pts, step_m, h_m, r_m, both, offset_m}]"""
    ox, oy = F.to_utm.transform(*spec['origin'])
    B = Builder(F, ground_m, exag, spec.get('exaggeration', 2.0), (ox, oy), seed=spec.get('seed', 7), detail=spec.get('detail', 'medium'))
    B.types = spec.get('types') or {}   # complete (house_types, which the caller runs)
    for fb in spec.get('fabric', []):   # (a typ that is neither would leave its lots empty without a word)
        if fb.get('typ', 'courtyard') not in BUILTIN_TYPES and fb.get('typ') not in B.types:
            raise SystemExit(f'citygen: fabric typ {fb.get("typ")!r} is not a house type: built in ({", ".join(BUILTIN_TYPES)}) or declared (docs/MODEL.md "House types")')
    wall_polys = []
    for wi, w in enumerate(spec.get('walls', [])):
        B.group(('walls', wi))
        ring = to_utm_ring(F, w['ring']) if 'ring' in w else to_utm_ring(F, osm_rings(w['osm'])[0])
        gates = [tuple(F.to_utm.transform(*g[:2])) + tuple(g[2:]) for g in w.get('gates', [])]   # [lon, lat] or [lon, lat, pier width m]
        B.walls(ring, h=w.get('h_m', 10), t=w.get('t_m', 10), gates=gates, towers=w.get('towers', True), gate_style=w.get('style', 'tower'), moat=w.get('moat'),
                moat_w=w.get('moat_w_m', 16.0), moat_off=w.get('moat_off_m'))
        wall_polys.append(Polygon(ring))
    inside = unary_union([p.buffer(-14) for p in wall_polys]) if wall_polys else None
    # landmarks first (their footprints are kept clear of fabric)
    lm_foot = []
    HEX0 = B.hex
    for li, L in enumerate(spec.get('landmarks', [])):
        B.group(('landmarks', li))   # one landmark rises as one piece (kilns, huts, boats: one piece each, below)
        if 'lon' in L: x, y = F.to_utm.transform(L['lon'], L['lat'])
        elif 'from' in L: x, y = F.to_utm.transform(*L['from'])
        else: x, y = F.to_utm.transform(*L['pts'][0])
        th = math.radians(L.get('theta_deg', spec.get('theta_deg', 0)))
        k = L['kind']
        B.hex = float(L.get('exaggeration', HEX0))   # a landmark built after a drawn elevation can keep nearer its true proportions
        if k == 'temple': B.compound(x, y, th, L.get('w_m', 70), L.get('d_m', 130), L.get('halls', [(-.25, .5, .16, 9, 'xieshan'), (.05, .6, .2, 13, 'double'), (.32, .55, .16, 10, 'xieshan')]))
        elif k == 'office': B.compound(x, y, th, L.get('w_m', 80), L.get('d_m', 110), L.get('halls', [(-.2, .55, .18, 8, 'xieshan'), (.15, .6, .2, 9, 'hip')]))
        elif k == 'palace': B.compound(x, y, th, L.get('w_m', 160), L.get('d_m', 200), L.get('halls', [(-.25, .5, .16, 12, 'xieshan'), (.05, .6, .2, 16, 'double_hip'), (.3, .5, .16, 12, 'xieshan')]), wall_h=L.get('wall_h', 6), side_halls=L.get('w_m', 160) < 400)
        elif k == 'belltower': B.bell_tower(x, y, th, L.get('w_m', 22))
        elif k == 'pagoda': B.pagoda(x, y, L.get('h_m', 40), L.get('w_m', 12), L.get('storeys', 7))
        elif k == 'front_hall': B.front_hall(x, y, th, L.get('w_m', 200), L.get('d_m', 400), tuple(tuple(q) for q in L.get('tiers', ((140, 200, 3.0), (120, 180, 8.0), (110, 165, 15.0)))))
        elif k == 'court': B.court(x, y, th, L['w_m'], L['d_m'], tuple(L.get('main', (.6, .2, 14, 'hip'))), tuple(L['north']) if L.get('north') else None, L.get('wings', True), L.get('wall_h', 4.0))
        elif k == 'armoury': B.armoury(x, y, th, L.get('w_m', 710), L.get('d_m', 322))
        elif k == 'market': B.market(x, y, th, L['w_m'], L['d_m'], lanes=L.get('lanes', 2))
        elif k == 'workshops': B.workshops(x, y, th, L['w_m'], L['d_m'], L.get('kilns', 33))
        elif k == 'pool_ring': B._emit(BOX, x, y, th, 0, L['w_m'], L['d_m'], .3, part=WATER)
        elif k == 'taixie': B.taixie(x, y, th, L['w_m'], L['d_m'], L['h_m'], tuple(L.get('rooms', (5, 2))), L.get('upper'), L.get('mirror_m', 0.0), roof_main=L.get('roof', 'hip'))
        elif k == 'terrace': B.terrace(x, y, th, L['w_m'], L['d_m'], L['h_m'], L.get('tiers', 3), L.get('top', .55), [tuple(hh) for hh in L.get('halls', [(0, 0, .7, .6, 14, 'double')])])
        elif k == 'hall': B.hall(x, y, th, L['w_m'], L['d_m'], L['h_m'], roof=L.get('roof', 'xieshan'), podium=L.get('podium', 0))
        elif k == 'paifang': B.paifang(x, y, th, L.get('w_m', 12), L.get('h_m', 8)); continue
        elif k == 'kilns':   # a workshop quarter: kilns (domes) and sheds scattered in a radius
            for i in range(L.get('n', 20)):
                B.group()
                a_ = B.rng.random() * math.tau; r_ = math.sqrt(B.rng.random()) * L.get('r_m', 150); kx, ky = x + r_ * math.cos(a_), y + r_ * math.sin(a_)
                if B.rng.random() < .55:
                    B.kiln(kx, ky, a_, g=ground_m(kx, ky))
                else: B.gable_house(kx, ky, th + B.rng.uniform(-.4, .4), B.rng.uniform(9, 16), B.rng.uniform(5, 7), B.rng.uniform(4, 5.5), part=FAB)
            continue
        elif k == 'pool': B._emit(BOX, x, y, th, 0, L['w_m'], L['d_m'], .3, part=WATER)
        elif k == 'platform':   # a bare rammed-earth platform (e.g. the Epang front hall: never finished), walls on the given sides
            gp_ = B.gsite(x, y, th, L['w_m'], L['d_m']); B._emit(FRUSTUM, x, y, th, 0, L['w_m'], L['d_m'], L['h_m'], L['w_m'] * .985, L['d_m'] * .97, part=EARTH, g_m=gp_); B.found = 0.0
            P = B.frame(x, y, th); hw, hd = L['w_m'] * .49, L['d_m'] * .48
            ends = {'north': ((-hw, hd), (hw, hd)), 'south': ((-hw, -hd), (hw, -hd)), 'east': ((hw, -hd), (hw, hd)), 'west': ((-hw, -hd), (-hw, hd))}
            for side in L.get('walls', []):
                (ax_, ay_), (bx_, by_) = ends[side]; B.strip(P(ax_, ay_), P(bx_, by_), L.get('wall_t', 8), L.get('wall_h', 6), part=WALL, z0=L['h_m'], g=gp_)
        elif k == 'ditch':   # a dug ditch along a polyline (dark water-like strip)
            pts_ = [F.to_utm.transform(*q) for q in L['pts']]
            for a, b in zip(pts_[:-1], pts_[1:]): B.strip(a, b, L.get('w_m', 12), .25, part=WATER)
            lm_foot.append(LineString(pts_).buffer(L.get('w_m', 12) / 2 + 8)); continue
        elif k == 'factory': B.factory(x, y, th, L['w_m'], L['d_m'], L.get('bays', 8), L.get('h_m', 10))
        elif k == 'chimney': B.chimney(x, y, L.get('h_m', 55))
        elif k == 'station':
            B.hall(x, y, th, L.get('w_m', 70), L.get('d_m', 20), L.get('h_m', 12), roof='hip', podium=1.0, front=1)
            P = B.frame(x, y, th); W_ = L.get('w_m', 70)
            for k_ in (1, 2):
                px, py = P(0, -22 * k_); B._emit(BOX, px, py, th, 3.5, W_ * 2.2, 7, .5, part=ROOF)   # platform canopies
                for i in range(9):
                    qx, qy = P(-W_ * 1.05 + i * W_ * 2.1 / 8, -22 * k_); B._emit(BOX, qx, qy, th, 0, .5, .5, 3.5, part=LMK)
        elif k == 'tower': B._emit(BOX, x, y, th, 0, L['w_m'], L.get('d_m', L['w_m']), L['h_m'], part=LMK)
        elif k == 'corridor':
            a = F.to_utm.transform(*L['from']); b = F.to_utm.transform(*L['to']); B.walkway(a, b, L.get('h_m', 9), L.get('w_m', 5)); continue
        elif k == 'bridge':
            a = F.to_utm.transform(*L['from']); b = F.to_utm.transform(*L['to'])
            Ln = math.hypot(b[0] - a[0], b[1] - a[1]); th_ = math.atan2(b[1] - a[1], b[0] - a[0]); g = max(ground_m(*a), ground_m(*b))   # the deck clears both banks
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; bw = L.get('w_m', 14); bh = L.get('h_m', 8)
            B._emit(BOX, mx, my, th_, bh, Ln, bw, 1.8, part=BRIDGE, g_m=g)
            if B.det >= 1:
                for k_ in (-1, 1): B._emit(BOX, mx - math.sin(th_) * k_ * bw * .47, my + math.cos(th_) * k_ * bw * .47, th_, bh + 1.8, Ln, .4, 1.1, part=BRIDGE, g_m=g)
            n = L.get('spans', max(4, int(Ln // 20)))
            for i in range(n + 1):
                q = i / n; px_, py_ = a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q; gq = ground_m(px_, py_)   # each pier from its own riverbed up to the deck
                B._emit(BOX, px_, py_, th_, -2, 2.6, bw * .9, bh + 2 + (g - gq), part=BRIDGE, g_m=gq)
            continue
        elif k == 'boats':
            a = F.to_utm.transform(*L['from']); b = F.to_utm.transform(*L['to'])
            th_ = math.atan2(b[1] - a[1], b[0] - a[0]); g = min(ground_m(*a), ground_m(*b))
            for i in range(L.get('n', 6)):
                B.group(); q = (i + .5) / L.get('n', 6); bx, by = a[0] + (b[0] - a[0]) * q + B.rng.uniform(-25, 25), a[1] + (b[1] - a[1]) * q + B.rng.uniform(-25, 25)
                ang = th_ + B.rng.uniform(-.3, .3); P_ = B.frame(bx, by, ang)
                g = min(ground_m(*q_) for q_ in ((bx, by), P_(-9, -2.5), P_(9, -2.5), P_(9, 2.5), P_(-9, 2.5)))   # afloat: the lowest ground under the hull
                B._emit(FRUSTUM, bx, by, ang, 0, 18, 5, 2, 15, 3.6, part=BRIDGE, g_m=g)
                B.roof(bx, by, ang, 2.2, 6, 3, 1.6, 'gable', part=ROOF, g=g, o=.3)
                if B.det >= 1: B._emit(CYL, bx, by, 0, 2, .15, 0, 9, part=BRIDGE, g_m=g)
            continue
        elif k == 'village':
            for i in range(L.get('n', 40)):
                a_ = B.rng.random() * math.tau; r_ = math.sqrt(B.rng.random()) * L.get('r_m', 140)
                if r_ < 30: r_ += 30   # the open ground in the middle
                B.group(); B.hut(x + r_ * math.cos(a_), y + r_ * math.sin(a_), B.rng.uniform(2.8, 4.2), B.rng.uniform(3.6, 5.0))
            B.group(); B.hall(x - 45, y + 10, 0, 18, 14, 7, roof='hip', cols=False)   # the large house
            if B.det >= 1:   # kilns on the edge
                for i in range(6):
                    B.group(); a_ = B.rng.random() * math.tau; r_ = L.get('r_m', 140) * 1.05
                    B._emit(CYL, x + r_ * math.cos(a_), y + r_ * math.sin(a_), 0, 0, 2.2, 0, 1.6, part=EARTH)
            continue
        if k == 'palace' and L.get('w_m', 0) > 400:   # a large palace city: keep only its halls clear, its courts get filled with buildings
            P = B.frame(x, y, th)
            for ly, fw, fd, hh, roof in L.get('halls', []):
                hx, hy = P(0, ly * L['d_m'])
                lm_foot.append(Point(hx, hy).buffer(max(fw * L['w_m'], fd * L['d_m']) * .8))
            corners = [P(-L['w_m'] / 2, -L['d_m'] / 2), P(L['w_m'] / 2, -L['d_m'] / 2), P(L['w_m'] / 2, L['d_m'] / 2), P(-L['w_m'] / 2, L['d_m'] / 2)]
            lm_foot.append(Polygon(corners).exterior.buffer(14))
        else:   # the landmark's own rectangle (rotated) plus a small apron
            P = B.frame(x, y, th); hw, hd = L.get('w_m', 30) / 2, L.get('d_m', L.get('w_m', 30)) / 2
            if k == 'taixie': hw = hw * (2 if L.get('mirror_m') else 1) + L.get('mirror_m', 0) / 2 + 4; hd += L.get('h_m', 6) * 1.1 + 4   # the twin, the walks, the stair
            if k == 'front_hall': hw += 12; hd += 14
            if k in ('armoury', 'market', 'court'): hw += 2; hd += 2
            lm_foot.append(Polygon([P(-hw, -hd), P(hw, -hd), P(hw, hd), P(-hw, hd)]).buffer(6))
    B.hex = HEX0
    lm_union = unary_union(lm_foot) if lm_foot else None
    shop_feet = []
    # lanes first (a paved grid inside the walls or a region, stopping at compound walls), then main streets with their shop rows
    street_geoms = []
    lanes = spec.get('lanes')
    if lanes:
        reg = inside if lanes.get('region', 'walls') == 'walls' else Polygon(to_utm_ring(F, lanes['region']))
        if reg is not None and lm_union is not None: reg = reg.difference(lm_union)   # lanes stop at compound walls
        if reg is not None and not reg.is_empty:
            th = math.radians(lanes.get('theta_deg', spec.get('theta_deg', 0)))
            cx, cy = reg.centroid.x, reg.centroid.y; R = affinity.rotate(reg, -th, origin=(cx, cy), use_radians=True)
            x0, y0, x1, y1 = R.bounds; sp = lanes['spacing_m']; lw = lanes.get('w_m', 6)
            ls = [LineString([(x, y0 - 10), (x, y1 + 10)]) for x in np.arange(x0 + sp, x1, sp)] + [LineString([(x0 - 10, y), (x1 + 10, y)]) for y in np.arange(y0 + sp * .7, y1, sp * .7)]
            for l in ls:
                for seg in _lines(affinity.rotate(l, th, origin=(cx, cy), use_radians=True).intersection(reg)):
                    cs_ = list(seg.coords)
                    for a, b in zip(cs_[:-1], cs_[1:]): B.group(('lanes', 0)); B.strip(a, b, lw, .1, part=PAVE)
            grid = unary_union([l.buffer(lw / 2, cap_style=2) for l in ls])
            street_geoms.append(affinity.rotate(grid, th, origin=(cx, cy), use_radians=True).intersection(reg))
    main_streets = [LineString([F.to_utm.transform(*p) for p in st['pts']]).buffer(st.get('w_m', 14) / 2, cap_style=2) for st in spec.get('streets', [])]
    wall_bands = [Polygon(to_utm_ring(F, w['ring'])).exterior.buffer(w.get('t_m', 10) * 1.6 + 6) for w in spec.get('walls', []) if 'ring' in w]
    shop_avoid = unary_union(([lm_union] if lm_union is not None else []) + street_geoms + main_streets + wall_bands + ([extra_avoid] if extra_avoid is not None else [])) if (lm_union is not None or street_geoms or main_streets or wall_bands or extra_avoid is not None) else None
    # streets: explicit main streets (paved, optional shop rows) + an oriented lane grid (paved) inside the walls or a region
    for si, st in enumerate(spec.get('streets', [])):
        pts = [F.to_utm.transform(*p) for p in st['pts']]
        street_geoms.append(LineString(pts).buffer(st.get('w_m', 14) / 2, cap_style=2))
        for a, b in zip(pts[:-1], pts[1:]):
            B.group(('streets', si)); B.strip(a, b, st.get('w_m', 14), .14, part=PAVE)
            if st.get('lanes3'):   # a Han avenue in three lanes (the middle one the emperor's): a lighter middle lane, side ditches (han_changan.md §3)
                B.strip(a, b, st.get('w_m', 14) / 3, .2, part=EARTH)
                L_ = math.hypot(b[0] - a[0], b[1] - a[1]) or 1; nx_, ny_ = -(b[1] - a[1]) / L_, (b[0] - a[0]) / L_
                for k_ in (-1, 1):
                    o_ = k_ * (st.get('w_m', 14) / 2 + 1.2); B.strip((a[0] + nx_ * o_, a[1] + ny_ * o_), (b[0] + nx_ * o_, b[1] + ny_ * o_), 1.6, .1, part=WATER)
            if st.get('shops'):
                for side in (1, -1): shop_feet.extend(B.shophouses(a, b, depth=st.get('shop_depth', 14), frontage=st.get('frontage', 7), h=st.get('shop_h', 7.5), side=side, gap=.08, street_w=st.get('w_m', 14), avoid=shop_avoid))
    streets = unary_union(street_geoms) if street_geoms else Polygon()
    avoid = unary_union(lm_foot + shop_feet + [streets] + ([extra_avoid] if extra_avoid is not None else [])) if (lm_foot or shop_feet or not streets.is_empty or extra_avoid is not None) else None
    wall_strips = unary_union([Polygon(to_utm_ring(F, w['ring'])).exterior.buffer(w.get('t_m', 10) * 1.2 + 10) for w in spec.get('walls', []) if 'ring' in w]) if spec.get('walls') else None
    for fi, fb in enumerate(spec.get('fabric', [])):
        B.group(('fabric', fi))
        if fb.get('region', 'walls') == 'walls': reg = inside
        elif isinstance(fb['region'], str) and fb['region'].startswith('osm:'): reg = Polygon(to_utm_ring(F, osm_rings(fb['region'][4:])[0])).buffer(-10)
        else: reg = Polygon(to_utm_ring(F, fb['region']))
        if reg is None: continue
        if wall_strips is not None and not wall_strips.is_empty: reg = reg.difference(wall_strips)   # no house on or against a city wall
        th = math.radians(fb.get('theta_deg', spec.get('theta_deg', 0)))
        det0 = B.det; B.det = DETAIL.get(fb.get('detail'), det0)   # a fabric seen only from the air can drop the doors and yard walls
        if fb.get('typ') == 'wards':   # walled wards (闾里) on a grid of `ward_m` squares, streets between them
            wm = fb.get('ward_m', 300); sw = fb.get('ward_street_m', 14); x0_, y0_, x1_, y1_ = reg.bounds
            for wx in np.arange(x0_, x1_ - wm * .5, wm + sw):
                for wy in np.arange(y0_, y1_ - wm * .5, wm + sw):
                    cell = shapely.box(wx, wy, wx + wm, wy + wm).intersection(reg)
                    if avoid is not None: cell = cell.difference(avoid)
                    if cell.is_empty or cell.area < .55 * wm * wm or cell.geom_type != 'Polygon': continue
                    B.group(('fabric', fi)); B.ward(cell, th, tuple(fb.get('lot', [22, 28])), fb.get('h_m', 6), empty=fb.get('empty', .08))
        else:
            B.fill(reg, th, tuple(fb.get('lot', [18, 26])), fb.get('typ', 'courtyard'), fb.get('h_m', 6), fb.get('empty', .06), avoid=avoid, scatter=fb.get('scatter', 0.0))
        B.det = det0
    bodies = None   # what stands on the ground by now (model xz): a row of trees steps over a house, a hall or a terrace on its line
    if spec.get('trees'):
        S_ = F.scale; rects = []
        for p in B.prims:
            if p[0] in (BOX, FRUSTUM) and p[11] in (FAB, LMK, EARTH) and p[7] > 1.0 * S_ * B.hex:
                c_, s_ = math.cos(p[3]), math.sin(p[3]); hw, hd = max(p[5], p[8] if p[0] == FRUSTUM else 0) / 2, max(p[6], p[9] if p[0] == FRUSTUM else 0) / 2
                rects.append(Polygon([(p[1] + x * c_ - z * s_, p[2] + x * s_ + z * c_) for x, z in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd))]))
        bodies = (shapely.STRtree(rects), rects) if rects else None
    for ti, tr in enumerate(spec.get('trees', [])):
        B.group(('trees', ti))
        pts = [F.to_utm.transform(*p) for p in tr['pts']]
        line = LineString(pts); n = tr.get('n', int(line.length // tr.get('step_m', 18)))
        for i in range(n):
            p = line.interpolate(i / max(1, n - 1), normalized=True)
            for side in (-1, 1):
                if tr.get('both', True) or side == 1:
                    off = tr.get('offset_m', 9) * side
                    q = line.interpolate(min(line.length, line.project(p) + 1)); th = math.atan2(q.y - p.y, q.x - p.x)
                    tx_, ty_ = p.x - math.sin(th) * off, p.y + math.cos(th) * off
                    if bodies is not None:
                        pt = Point(*F.model(tx_, ty_))
                        if any(bodies[1][j].buffer(1.5 * F.scale).contains(pt) for j in bodies[0].query(pt.buffer(2 * F.scale))):
                            for _ in range(3): B.rng.random()   # the draws tree() would take: the rest of the city stays as it was
                            continue
                    B.group(); B.tree(tx_, ty_, tr.get('h_m', 11), tr.get('r_m', 4), tr.get('kind', 'willow'))
    return B.finish(spec.get('rank_noise', .08), meta)
