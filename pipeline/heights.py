"""Building heights after the primary adapter, in three opt-in layers (buildings keys in city.yaml, docs/DATA.md), in this order:

1. height_correction: an outside footprint dataset with heights (3D-GloBFP, pipeline/globfp.py) corrects each primary building
   by the overlap-area-weighted median of its heights, where it covers enough of the footprint (correction).
2. height_supplement: spatially matched public OSM building heights raise, and with `lower: true` also lower, a primary
   building (supplement); optional whole tall buildings missing from the primary footprints (fill_gaps).
3. height_zones: researched polygons of a known height or storey range, labelled schematic (zones).

The primary footprint, order, year, age method and function are preserved. One mapped whole building can change at most one
primary footprint; roof / antenna / other building parts are not whole-building height references. Explicit height beats a
storey estimate. A missing, ambiguous or distant reference leaves the primary height unchanged. No network in prep: fetch the
area's building_heights theme with pipeline/osm.py and the dataset's cells with pipeline/globfp.py first. Every change is kept
per building in build/data/building_heights.json (before and after, layer by layer); tools/heightcheck.py scores the result.

  python -I pipeline/heights.py selftest
  python -I pipeline/heights.py inspect <city_dir>     (mapped towers >=200m against the prepared footprints)
"""
import collections, json, math, os, re, sys

from shapely.strtree import STRtree


def metres(value):
    """OSM height: metres by default, metric units, ft, or feet/inches. Reject ranges and multiple values."""
    if value is None or isinstance(value, bool): return None
    s = str(value).strip().lower()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*'\s*(?:(\d+(?:\.\d+)?)\s*\")?", s)
    if m:
        inches = float(m[2] or 0)
        h = (float(m[1]) + inches / 12) * .3048 if inches < 12 else None
    else:
        m = re.fullmatch(r'(\d+(?:\.\d+)?)\s*(m|metres?|meters?|cm|ft|feet)?', s)
        if not m: return None
        h = float(m[1]) * {'cm': .01, 'ft': .3048, 'feet': .3048}.get(m[2], 1)
    return h if h is not None and math.isfinite(h) and 0 < h <= 2000 else None


def levels(tags):
    """OSM building:levels as a whole positive storey count above ground, or None (ranges, fractions, lists refused)"""
    s = str(tags.get('building:levels', '')).strip()
    return float(s) if re.fullmatch(r'\d+(?:\.0+)?', s) and 0 < float(s) <= 300 else None


def height(tags, floor_height_m=3.2):
    """A height tag is the top above ground, not an addition to min_height. Storeys remain an estimate."""
    h = metres(tags.get('height'))
    if h is not None: return h, 'height', tags['height'], 'estimat' in tags.get('source:height', '').lower()
    n = levels(tags)
    if n is not None: return n * floor_height_m, 'building:levels', tags['building:levels'], True
    return None


def references(city, frame, floor_height_m=3.2):
    import layout, osm, osmgeo
    path = osm.cache_path(layout.raw(city), frame.area, 'building_heights')
    if not os.path.isfile(path):
        raise SystemExit(f'heights: no OSM heights for this area; run pipeline/osm.py {city} building_heights')
    data = json.load(open(path, encoding='utf-8')); out = []; skipped = collections.Counter()
    for e in data['elements']:
        t = e.get('tags', {})
        if not t.get('building') or t['building'] in ('no', 'construction', 'proposed', 'demolished', 'ruins'):
            skipped['not_existing_whole_building'] += 1; continue
        if t.get('building:part', 'no') != 'no':
            skipped['building_part'] += 1; continue
        got = height(t, floor_height_m)
        if got is None: skipped['invalid_height_and_levels'] += 1; continue
        h, field, raw, estimate = got
        for k, p in enumerate(osmgeo.polys(e, frame.to_utm.transform)):
            if p.geom_type != 'Polygon' or p.is_empty or not p.is_valid or p.area <= 0:
                skipped['invalid_polygon'] += 1; continue
            meta = {'source': 'OSM ' + field, 'id': f'{e["type"]}/{e["id"]}', 'name': t.get('name') or t.get('name:en'),
                    'url': f'https://www.openstreetmap.org/{e["type"]}/{e["id"]}', 'field': field, 'value': raw,
                    'height_m': h, 'estimated': estimate, 'source_height': t.get('source:height')}
            if field == 'building:levels': meta['floor_height_m'] = floor_height_m
            out.append({'poly': p, 'meta': meta, 'component': k})
    return out, {'source': 'OpenStreetMap', 'licence': 'ODbL-1.0', 'cache': os.path.basename(path),
                 'snapshot': data.get('osm3s', {}).get('timestamp_osm_base'), 'references': len(out), 'skipped': dict(skipped)}


def match_candidates(q, polys, tree):
    """Conservative geometry scores shared by height and appearance adapters; no height or date decision here."""
    hits = []
    for i in tree.query(q, predicate='intersects'):
        i = int(i); p = polys[i]
        if not p.buffer(3).covers(q.centroid): continue
        area = p.intersection(q).area
        cover = area / min(p.area, q.area); ratio = min(p.area, q.area) / max(p.area, q.area)
        iou = area / (p.area + q.area - area)
        if cover >= .7 and ratio >= .25 and iou >= .35: hits.append((iou, i))
    return sorted(hits, reverse=True)


def supplement(buildings, refs, lower=False):
    """Return the same adapter records with raised heights and indexed provenance, plus matching counts. lower: a matched
    reference also lowers a primary that stands higher (both ways, height_supplement.lower), counted apart.

    Match a reference's centre to a containing primary polygon (3m mapping tolerance), with >=70% overlap of the smaller
    footprint, >=1/4 area ratio and >=35% IoU. The strongest overlap wins; nearly tied overlaps or conflicting nearly tied
    whole-building references are refused. There is no nearest-building fallback across a street or onto a podium.
    """
    rows = list(buildings); polys = [b[0] for b in rows]; tree = STRtree(polys)
    candidates = collections.defaultdict(list); counts = collections.Counter(); unmatched = []
    for r in refs:
        q = r['poly']; hits = match_candidates(q, polys, tree)
        if not hits or len(hits) > 1 and hits[0][0] - hits[1][0] < .05:
            counts['ambiguous' if hits else 'unmatched'] += 1
            if r['meta']['height_m'] >= 200: unmatched.append(r['meta'])
            continue
        score, i = hits[0]; candidates[i].append((r['meta']['field'] == 'height', score, r))
    selected = {}; changes = []
    for i, options in candidates.items():
        options.sort(key=lambda x: (x[0], x[1]), reverse=True)
        explicit, score, r = options[0]; m = r['meta']; old = rows[i][1]
        if len(options) > 1:
            other = options[1]
            if other[0] == explicit and score - other[1] < .05 and abs(m['height_m'] - other[2]['meta']['height_m']) > 10:
                counts['conflicting'] += 1; continue
        counts['matched'] += 1
        if m['height_m'] == old or m['height_m'] < old and not lower: counts['primary_kept'] += 1; continue
        selected[i] = {**m, 'primary_height_m': old, 'match_iou': round(score, 4)}
        p, _, year, how, func = rows[i]
        rows[i] = p, m['height_m'], year, how, func
        changes.append({'bi': i, **selected[i]}); counts['raised' if m['height_m'] > old else 'lowered'] += 1; counts[m['source']] += 1
    return rows, selected, {'counts': dict(counts), 'changes': changes,
                            'unmatched_tall': sorted(unmatched, key=lambda x: -x['height_m'])}


def load(city, frame, buildings, settings):
    """The opt-in prep adapter. New cities use configuration, never a city name or tower-specific code."""
    if settings.get('source', 'osm') != 'osm': raise SystemExit('heights: height_supplement.source must be osm')
    floor = float(settings.get('floor_height_m', 3.2))
    if not math.isfinite(floor) or not 2 <= floor <= 6: raise SystemExit('heights: floor_height_m must be between 2 and 6 metres')
    lower = settings.get('lower', False)
    if not isinstance(lower, bool): raise SystemExit('heights: height_supplement.lower must be true or false')
    refs, provenance = references(city, frame, floor)
    excluded = set(settings.get('exclude_osm', []))
    if excluded:
        refs = [r for r in refs if r['meta']['id'] not in excluded]
        provenance['excluded_osm'] = sorted(excluded)
    rows, selected, result = supplement(buildings, refs, lower)
    if lower: result['lower'] = True
    fill = settings.get('fill_gaps')
    if fill:
        added, metadata, report = gap_buildings(rows, refs, frame, fill)
        offset = len(rows)
        rows.extend(added)
        selected.update({offset + i: m for i, m in enumerate(metadata)})
        result['fill_gaps'] = report
    result.update(provenance)
    print(f'heights: {len(refs)} OSM references; {json.dumps(result["counts"], ensure_ascii=False)}')
    return rows, selected, result


def correct(buildings, geoms, values, min_cover=.3):
    """Each primary building takes the overlap-area-weighted median of the dataset's heights over it, where the dataset's
    footprints cover at least min_cover of its area; otherwise it keeps its height. -> (rows, the layer's record)"""
    import numpy as np, shapely
    rows = list(buildings); P = np.array([b[0] for b in rows], dtype=object)
    pi, gi = STRtree(geoms).query(P, predicate='intersects') if len(rows) and len(geoms) else (np.zeros(0, int),) * 2
    a = shapely.area(shapely.intersection(P[pi], geoms[gi])) if len(pi) else np.zeros(0)
    keep = a > 0; pi, gi, a = pi[keep], gi[keep], a[keep]
    order = np.lexsort((values[gi], pi)); pi, gi, a = pi[order], gi[order], a[order]   # by building, then by height
    starts = np.searchsorted(pi, np.arange(len(rows))); ends = np.searchsorted(pi, np.arange(len(rows)), side='right')
    area = shapely.area(P) if len(rows) else np.zeros(0)
    counts = collections.Counter(); rec = {'bi': [], 'before': [], 'after': [], 'cover': []}
    for i in range(len(rows)):
        s, e = starts[i], ends[i]
        if s == e: counts['no_cover'] += 1; continue
        cover = float(a[s:e].sum() / area[i])
        if cover < min_cover: counts['low_cover'] += 1; continue
        w = np.cumsum(a[s:e]); h = float(values[gi[s + int(np.searchsorted(w, w[-1] / 2))]])
        p, old, year, how, func = rows[i]
        counts['corrected'] += 1; counts['raised' if h > old else 'lowered' if h < old else 'unchanged'] += 1
        rows[i] = p, h, year, how, func
        for k, v in (('bi', i), ('before', round(old, 2)), ('after', round(h, 2)), ('cover', round(min(cover, 9.999), 3))): rec[k].append(v)
    return rows, {'min_cover': min_cover, 'counts': dict(counts), **rec}


def correction(city, frame, buildings, settings):
    """The height_correction layer: settings {source: globfp, min_cover: 0.3}"""
    unknown = set(settings) - {'source', 'min_cover'}
    if unknown: raise SystemExit(f'heights: height_correction: unknown keys {sorted(unknown)}')
    if settings.get('source', 'globfp') != 'globfp': raise SystemExit('heights: height_correction.source must be globfp')
    cover = settings.get('min_cover', .3)
    if isinstance(cover, bool) or not isinstance(cover, (int, float)) or not 0 < cover <= 1:
        raise SystemExit('heights: height_correction.min_cover must be in (0, 1]')
    import globfp, local
    geoms, values, provenance = globfp.load(local.raw(), frame)
    rows, rec = correct(buildings, geoms, values, float(cover))
    print(f'height correction: {provenance["footprints"]} {provenance["dataset"]} footprints; {json.dumps(rec["counts"])}')
    return rows, {**provenance, **rec}


def zone_unit(c):
    """a building's own number in [0, 1), from its centroid (the same every run; a salt of its own, apart from prep's year spread)"""
    import hashlib
    return int(hashlib.md5(f'zone:{c.x:.0f},{c.y:.0f}'.encode()).hexdigest()[:8], 16) / 2 ** 32


def zone_height(zone, c):
    """the zone's height for the building with centroid c: a fixed height, a height range, storeys or a storey range"""
    u = zone_unit(c)
    if 'height_m' in zone:
        lo, hi = zone['height_m']; return round(lo + u * (hi - lo), 1)
    lo, hi = zone['storeys']; return round(min(hi, lo + int(u * (hi - lo + 1))) * zone['floor_height_m'], 1)


def zones(city, frame, value):
    """the height_zones layer's zones: a list in city.yaml or a GeoJSON file in the city folder (a path relative to it), each a
    polygon in lon/lat with height_m or storeys (a number or [low, high]), source and label; floor_height_m defaults to 3.2"""
    from shapely.geometry import shape
    from shapely.ops import transform
    if isinstance(value, str):
        data = json.load(open(os.path.join(city, value), encoding='utf-8'))
        items = [{**(f.get('properties') or {}), 'geometry': f['geometry']} for f in data['features']]
    elif isinstance(value, list): items = [{**z, 'geometry': {'type': 'Polygon', 'coordinates': [z['polygon']]}} if 'polygon' in z else z for z in value]
    else: raise SystemExit('heights: height_zones must be a list of zones or a GeoJSON path in the city folder')
    out = []
    for k, z in enumerate(items):
        name = f'height_zones[{k}]'
        for key in ('source', 'label'):
            if not isinstance(z.get(key), str) or not z[key].strip(): raise SystemExit(f'heights: {name}: {key} (text) required')
        if ('height_m' in z) == ('storeys' in z): raise SystemExit(f'heights: {name}: exactly one of height_m and storeys')
        kind = 'height_m' if 'height_m' in z else 'storeys'; r = z[kind]
        r = [r, r] if isinstance(r, (int, float)) and not isinstance(r, bool) else r
        if (not isinstance(r, list) or len(r) != 2 or any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in r)
                or not 0 < r[0] <= r[1] or kind == 'storeys' and any(int(x) != x for x in r)):
            raise SystemExit(f'heights: {name}: {kind} a positive number or [low, high]' + (' (whole storeys)' if kind == 'storeys' else ''))
        floor = float(z.get('floor_height_m', 3.2))
        if not 2 <= floor <= 6: raise SystemExit(f'heights: {name}: floor_height_m between 2 and 6 metres')
        g = transform(frame.to_utm.transform, shape(z['geometry']))
        if g.is_empty or not g.is_valid or g.geom_type not in ('Polygon', 'MultiPolygon'): raise SystemExit(f'heights: {name}: a valid polygon required')
        out.append({'label': z['label'], 'source': z['source'], kind: [float(r[0]), float(r[1])] if kind == 'height_m' else [int(r[0]), int(r[1])],
                    'floor_height_m': floor, 'poly': g})
    return out


def apply_zones(buildings, zone_list, n=None):
    """Buildings whose centroid lies inside a zone take the zone's height (the first zone listed wins where zones overlap); only
    the first n rows (the primary's) take part: gap-fill additions are mapped towers with their own heights. -> (rows, record)"""
    from shapely.prepared import prep as prepared
    rows = list(buildings); n = len(rows) if n is None else n
    shapes = [prepared(z['poly']) for z in zone_list]; tree = STRtree([z['poly'] for z in zone_list]) if zone_list else None
    rec = {'bi': [], 'before': [], 'after': [], 'zone': []}; per = collections.Counter()
    for i in range(n if tree is not None else 0):
        p, old, year, how, func = rows[i]; c = p.centroid
        hit = sorted(int(k) for k in tree.query(c) if shapes[int(k)].contains(c))
        if not hit: continue
        z = zone_list[hit[0]]; h = zone_height(z, c)
        rows[i] = p, h, year, how, func; per[hit[0]] += 1
        for k, v in (('bi', i), ('before', round(old, 2)), ('after', h), ('zone', hit[0])): rec[k].append(v)
    listed = [{**{k: v for k, v in z.items() if k != 'poly'}, 'schematic': True, 'buildings': per[k]} for k, z in enumerate(zone_list)]
    return rows, {'zones': listed, 'counts': {'zoned': len(rec['bi'])}, **rec}


def apply(city, frame, buildings, config):
    """The opt-in height layers of city.yaml's buildings, in their order: correction, OSM supplement, zones.
    -> (rows, per-building height source {bi: meta} for stats, the sidecar). The supplement alone writes its sidecar as before."""
    if not config.get('height_correction') and not config.get('height_zones'):
        return load(city, frame, buildings, config['height_supplement'])
    rows = list(buildings); n = len(rows); meta, report, layers = {}, {}, {}
    if config.get('height_correction'):
        rows, rec = correction(city, frame, rows, config['height_correction']); layers['dataset'] = rec
        for i in rec['bi']: meta[i] = {'source': rec['dataset'], 'estimated': True, 'licence': rec['licence']}
    if config.get('height_supplement'):
        rows, selected, report = load(city, frame, rows, config['height_supplement']); meta.update(selected)
        ch = report['changes']
        layers['osm'] = {'counts': {k: report['counts'].get(k, 0) for k in ('matched', 'raised', 'lowered', 'primary_kept')},
                         'bi': [c['bi'] for c in ch], 'before': [round(c['primary_height_m'], 2) for c in ch],
                         'after': [round(c['height_m'], 2) for c in ch], 'source': [c['source'] for c in ch]}
    if config.get('height_zones'):
        rows, rec = apply_zones(rows, zones(city, frame, config['height_zones']), n); layers['zones'] = rec
        for i, k in zip(rec['bi'], rec['zone']):
            z = rec['zones'][k]
            meta[i] = {'source': 'height zone (schematic)', 'label': z['label'], 'zone_source': z['source'], 'schematic': True, 'estimated': True}
        print(f'height zones: {len(rec["zones"])} zones; {rec["counts"]["zoned"]} buildings take a schematic height')
    report['layers'] = layers
    return rows, meta, report


def gap_candidates(buildings, refs, frame, min_height_m=100, min_levels=30):
    """Whole tall buildings only on empty primary ground. Boundary contact also refuses a candidate; never clip a tower
    round an old footprint or transfer its height to a neighbour. Accepted OSM footprints cannot overlap each other either.
    """
    tree = STRtree([b[0] for b in buildings]); accepted = []; counts = collections.Counter()
    for r in sorted(refs, key=lambda x: (-x['meta']['height_m'], x['meta']['id'], x['component'])):
        p, m = r['poly'], r['meta']; c = p.centroid
        tall = m['height_m'] >= min_height_m or (m['field'] == 'building:levels' and float(m['value']) >= min_levels)
        if not tall: continue
        if not frame.inside(c.x, c.y): counts['outside_plate'] += 1; continue
        if len(tree.query(p, predicate='intersects')): counts['primary_overlap'] += 1; continue
        if any(p.intersects(q['poly']) for q in accepted): counts['duplicate_overlap'] += 1; continue
        accepted.append(r)
    return accepted, counts


def gap_buildings(buildings, refs, frame, settings):
    """Use the existing global-fallback age sampler; retain its 100m/five-year estimates, never OSM start_date."""
    import local, overture_ghsl
    mh = float(settings.get('min_height_m', 100)); ml = int(settings.get('min_levels', 30))
    threshold = float(settings.get('ghsl_threshold_m2', 1500))
    if not math.isfinite(mh) or mh <= 0 or ml <= 0 or not 0 < threshold <= 10000:
        raise SystemExit('heights: positive skyline thresholds and ghsl_threshold_m2 in (0,10000] required')
    candidates, counts = gap_candidates(buildings, refs, frame, mh, ml)
    points = [frame.ground_wgs(r['poly'].centroid.x, r['poly'].centroid.y) for r in candidates]
    years = overture_ghsl.first_epoch(local.raw(), points, frame.area, threshold) if points else []
    added, metadata = [], []
    for r, year in zip(candidates, years):
        if year is None:
            counts['no_ghsl_epoch'] += 1
            continue   # no invented date or undated filler when the cell has no threshold crossing
        m = {**r['meta'], 'footprint_source': 'OSM', 'age_source': 'GHSL R2023A GHS-BUILT-S',
             'age_method': 'epoch', 'epoch': year, 'age_estimated': True, 'age_resolution_m': 100,
             'ghsl_threshold_m2': threshold}
        added.append((r['poly'], m['height_m'], year, 'epoch', ''))
        metadata.append(m)
    counts['added'] = len(added)
    print(f'height gaps: {dict(counts)}; GHSL 100m / five-year estimates')
    return added, metadata, {'min_height_m': mh, 'min_levels': ml, 'counts': dict(counts),
                             'buildings': [{'offset': i, **m} for i, m in enumerate(metadata)]}


def inspect(city):
    """Explain unmatched skyline references without fetching, changing a model or relaxing the match rules."""
    import yaml, layout
    from geo import Frame
    from shapely.geometry import Polygon
    from shapely.affinity import affine_transform
    c = yaml.safe_load(open(os.path.join(city, 'city.yaml'), encoding='utf-8'))
    f = Frame(c['box'], 1 / c['scale']); m = json.load(open(layout.data(city, 'model.json')))
    # Inverse of Frame.model: a model's x is east and z is south, about the plate centre.
    inv = [1 / f.scale, 0, 0, -1 / f.scale, f.cx, f.cy]
    polys = [affine_transform(Polygon(p[2][0], p[2][1:]), inv) for p in m['p']]
    tree = STRtree(polys)
    refs, _ = references(city, f)
    for r in sorted(refs, key=lambda r: -r['meta']['height_m']):
        if r['meta']['height_m'] < 200: continue
        q = r['poly']; hits = []
        for i in tree.query(q.buffer(30), predicate='intersects'):
            i = int(i); p = polys[i]; a = p.intersection(q).area
            hits.append({'bi': m['p'][i][0], 'h': m['b'][m['p'][i][0]][1], 'area_m2': round(p.area),
                         'iou': round(a / (p.area + q.area - a), 3), 'cover': round(a / min(p.area, q.area), 3),
                         'centre_distance_m': round(p.distance(q.centroid), 1)})
        hits.sort(key=lambda x: (-x['iou'], x['centre_distance_m']))
        print(json.dumps({'reference': r['meta'], 'area_m2': round(q.area), 'candidates': hits[:3]}, ensure_ascii=False))


def selftest():
    import tempfile, unittest
    from unittest.mock import patch
    from shapely.geometry import box
    class Tests(unittest.TestCase):
        def test_units_and_ambiguous_tags(self):
            self.assertAlmostEqual(metres('100 ft'), 30.48)
            self.assertAlmostEqual(metres('7\'4"'), 2.2352)
            self.assertEqual(metres('632 m'), 632)
            for s in ('3-5', '30;50', '>20', '0,8', 'NaN', '-3', '9999', True): self.assertIsNone(metres(s))
        def test_height_before_estimated_levels(self):
            self.assertEqual(height({'height': '632', 'building:levels': '128', 'min_height': '20'})[:2], (632, 'height'))
            self.assertEqual(height({'building:levels': '10'})[0], 32)
            self.assertTrue(height({'building:levels': '10'})[3])
            self.assertIsNone(height({'building:levels': '10;12'}))
        def test_raise_only_and_preserve_years(self):
            p = box(0, 0, 20, 20); b = [(p, 12, 1987, 'seen', 'office')]
            ref = lambda h: [{'poly': p, 'meta': {'height_m': h, 'field': 'height', 'source': 'OSM height'}}]
            rows, selected, result = supplement(b, ref(632))
            self.assertEqual(rows[0], (p, 632, 1987, 'seen', 'office'))
            self.assertEqual(selected[0]['primary_height_m'], 12)
            self.assertEqual(supplement(b, ref(10))[0], b)
            self.assertEqual(supplement(b, [])[0], b)
        def test_lower_both_ways_counts_and_explicit_first(self):
            p = box(0, 0, 20, 20); b = [(p, 30, 1987, 'seen', 'office')]
            ref = lambda h, f='building:levels': {'poly': p, 'meta': {'height_m': h, 'field': f, 'source': 'OSM ' + f}}
            self.assertEqual(supplement(b, [ref(9.6)])[0], b)   # raise only by default
            rows, selected, result = supplement(b, [ref(9.6)], lower=True)
            self.assertEqual(rows[0], (p, 9.6, 1987, 'seen', 'office'))
            self.assertEqual(selected[0]['primary_height_m'], 30)
            self.assertEqual((result['counts']['lowered'], result['counts'].get('raised', 0)), (1, 0))
            self.assertEqual(supplement(b, [ref(30)], lower=True)[2]['counts']['primary_kept'], 1)
            self.assertEqual(supplement(b, [ref(12, 'height'), ref(6)], lower=True)[0][0][1], 12)
        def test_dataset_correction_weighted_median_and_cover(self):
            import numpy as np
            p = box(0, 0, 20, 10); q = box(100, 0, 110, 10); r = box(200, 0, 210, 10)
            b = [(p, 25, 1990, 'seen', ''), (q, 25, 1990, 'seen', ''), (r, 25, 1990, 'seen', '')]
            # p: three dataset buildings, 60% of the overlap at 9 m -> 9; q: 20% covered -> kept; r: nothing over it
            g = np.array([box(0, 0, 12, 10), box(12, 0, 16, 10), box(16, 0, 20, 10), box(100, 0, 102, 10)], dtype=object)
            v = np.array([9., 40., 30., 3.])
            rows, rec = correct(b, g, v, .3)
            self.assertEqual([x[1] for x in rows], [9, 25, 25])
            self.assertEqual(rows[0][2:], (1990, 'seen', ''))
            self.assertEqual((rec['bi'], rec['before'], rec['after'], rec['cover']), ([0], [25], [9], [1.0]))
            self.assertEqual(rec['counts'], {'corrected': 1, 'lowered': 1, 'low_cover': 1, 'no_cover': 1})
            self.assertEqual(correct(b, g, v, .1)[0][1][1], 3)
            self.assertEqual(correct(b, g[:0], v[:0], .3)[0], b)
        def test_zones_by_centroid_deterministic_and_labelled(self):
            from geo import Frame
            f = Frame((121.4, 31.2, 121.6, 31.4), .0001)
            x0, y0 = f.to_utm.transform(121.5, 31.3)
            ll = lambda x, y: list(f.to_utm.transform(x, y, direction='INVERSE'))
            ring = [ll(x0 + dx, y0 + dy) for dx, dy in ((0, 0), (300, 0), (300, 300), (0, 300), (0, 0))]
            Z = zones('.', f, [{'polygon': ring, 'storeys': [1, 3], 'source': 'a survey', 'label': 'old lanes'},
                               {'polygon': ring, 'height_m': 50, 'source': 'later', 'label': 'listed second'}])
            inside = [(box(x0 + k * 30, y0 + 10, x0 + k * 30 + 20, y0 + 30), 32, 1990, 'seen', '') for k in range(9)]
            out = [(box(x0 + 400, y0, x0 + 420, y0 + 20), 32, 1990, 'seen', '')]
            rows, rec = apply_zones(inside + out, Z)
            hs = [r[1] for r in rows]
            self.assertEqual(hs[-1], 32)
            self.assertTrue(all(h in (3.2, 6.4, 9.6) for h in hs[:-1]), hs)
            self.assertGreater(len(set(hs[:-1])), 1)
            self.assertEqual(apply_zones(inside + out, Z)[0], rows)
            self.assertEqual(rec['zones'][0]['buildings'], 9); self.assertTrue(rec['zones'][0]['schematic'])
            self.assertEqual(apply_zones(inside, Z, n=0)[0], inside)   # rows past n (gap fill) keep their heights
            for bad in ({'polygon': ring, 'source': 's', 'label': 'l'}, {'polygon': ring, 'storeys': 2, 'height_m': 5, 'source': 's', 'label': 'l'},
                        {'polygon': ring, 'storeys': [1.5, 2], 'source': 's', 'label': 'l'}, {'polygon': ring, 'storeys': 2, 'label': 'l'}):
                with self.assertRaises(SystemExit): zones('.', f, [bad])
        def test_layer_order_dataset_then_osm_then_zones(self):
            import numpy as np
            import globfp
            from types import SimpleNamespace
            p = box(0, 0, 20, 20); q = box(50, 0, 70, 20)
            b = [(p, 25, 1990, 'seen', ''), (q, 25, 1990, 'seen', '')]
            g = np.array([box(0, 0, 20, 20), box(50, 0, 70, 20)], dtype=object)
            ref = [{'poly': p, 'component': 0, 'meta': {'height_m': 9.6, 'field': 'building:levels', 'source': 'OSM building:levels', 'id': 'way/1'}}]
            zone = [{'label': 'z', 'source': 's', 'height_m': [7, 7], 'floor_height_m': 3.2, 'poly': box(40, -10, 80, 30)}]
            cfg = {'height_correction': {'source': 'globfp'}, 'height_supplement': {'lower': True}, 'height_zones': [{}]}
            f = SimpleNamespace(area=(0, 0, 1, 1))
            with patch.object(globfp, 'load', return_value=(g, np.array([40., 60.]), {'dataset': '3D-GloBFP', 'licence': 'CC BY 4.0', 'footprints': 2})), \
                 patch(__name__ + '.references', return_value=(ref, {})), patch(__name__ + '.zones', return_value=zone):
                rows, meta, report = apply('.', f, b, cfg)
            self.assertEqual([r[1] for r in rows], [9.6, 7])
            L = report['layers']
            self.assertEqual((L['dataset']['before'], L['dataset']['after']), ([25, 25], [40, 60]))
            self.assertEqual((L['osm']['bi'], L['osm']['before'], L['osm']['after']), ([0], [40], [9.6]))
            self.assertEqual((L['zones']['bi'], L['zones']['before'], L['zones']['after']), ([1], [60], [7]))
            self.assertEqual(meta[0]['source'], 'OSM building:levels'); self.assertTrue(meta[1]['schematic'])
        def test_neighbour_and_large_podium_not_raised(self):
            p = box(0, 0, 20, 20); q = box(19, 0, 39, 20)
            r = {'poly': q, 'meta': {'height_m': 632, 'field': 'height', 'source': 'OSM height'}}
            b = [(p, 12, 1987, 'seen', '')]
            self.assertFalse(supplement(b, [r])[1])
            r['poly'] = box(4, 4, 6, 6)
            self.assertFalse(supplement(b, [r])[1])
        def test_duplicate_primary_match_refused(self):
            p = box(0, 0, 20, 20); b = [(p, 12, 1987, 'seen', '')] * 2
            r = {'poly': p, 'meta': {'height_m': 632, 'field': 'height', 'source': 'OSM height'}}
            self.assertFalse(supplement(b, [r])[1])
        def test_explicit_height_beats_storey_estimate(self):
            p = box(0, 0, 20, 20); b = [(p, 12, 1987, 'seen', '')]
            refs = [{'poly': p, 'meta': {'height_m': h, 'field': f, 'source': 'OSM ' + f}}
                    for h, f in ((100, 'height'), (150, 'building:levels'))]
            self.assertEqual(supplement(b, refs)[0][0][1], 100)
        def test_conflicting_building_references_refused(self):
            p = box(0, 0, 20, 20); b = [(p, 12, 1987, 'seen', '')]
            refs = [{'poly': p, 'meta': {'height_m': h, 'field': 'height', 'source': 'OSM height'}} for h in (100, 200)]
            self.assertFalse(supplement(b, refs)[1])
        def test_cached_parts_construction_and_units(self):
            import osm
            from geo import Frame
            f = Frame((121.4, 31.2, 121.6, 31.4), .0001)
            ring = [{'lon': x, 'lat': y} for x, y in ((121.5, 31.3), (121.501, 31.3),
                    (121.501, 31.301), (121.5, 31.301), (121.5, 31.3))]
            tags = [{'building': 'yes', 'height': '100 ft'}, {'building:part': 'yes', 'height': '468'},
                    {'building': 'construction', 'height': '480'}, {'building': 'yes', 'building:levels': '12'}]
            data = {'elements': [{'type': 'way', 'id': i, 'tags': t, 'geometry': ring} for i, t in enumerate(tags)]}
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, 'osm.json'); json.dump(data, open(p, 'w'))
                with patch.object(osm, 'cache_path', return_value=p): refs, report = references(d, f)
            self.assertEqual(len(refs), 2)
            self.assertAlmostEqual(refs[0]['meta']['height_m'], 30.48)
            self.assertAlmostEqual(refs[1]['meta']['height_m'], 38.4)
            self.assertTrue(refs[1]['meta']['estimated'])
            self.assertEqual(report['skipped']['not_existing_whole_building'], 2)
        def test_gaps_refuse_even_small_overlap_and_boundary_contact(self):
            from types import SimpleNamespace
            f = SimpleNamespace(inside=lambda x, y: True)
            b = [(box(0, 0, 20, 20), 12, 1987, 'seen', '')]
            ref = lambda p, i: {'poly': p, 'component': 0, 'meta': {'id': i, 'height_m': 150, 'field': 'height'}}
            refs = [ref(box(19.99, 0, 40, 20), 'overlap'), ref(box(20, 0, 40, 20), 'touch'),
                    ref(box(50, 0, 70, 20), 'empty')]
            accepted, counts = gap_candidates(b, refs, f)
            self.assertEqual([r['meta']['id'] for r in accepted], ['empty'])
            self.assertEqual(counts['primary_overlap'], 2)
            self.assertEqual(b[0][2:], (1987, 'seen', ''))
        def test_gaps_do_not_duplicate_osm_or_add_low_buildings(self):
            from types import SimpleNamespace
            f = SimpleNamespace(inside=lambda x, y: x < 100)
            refs = [{'poly': box(x, 0, x+20, 20), 'component': 0,
                     'meta': {'id': i, 'height_m': h, 'field': 'height'}}
                    for i, x, h in (('a', 0, 150), ('duplicate', 0, 140), ('low', 50, 20), ('outside', 200, 150))]
            accepted, counts = gap_candidates([], refs, f)
            self.assertEqual([r['meta']['id'] for r in accepted], ['a'])
            self.assertEqual(counts['duplicate_overlap'], 1)
            self.assertEqual(counts['outside_plate'], 1)
        def test_gap_dates_use_existing_ghsl_sampler(self):
            import local, overture_ghsl
            from types import SimpleNamespace
            f = SimpleNamespace(inside=lambda x, y: True, area=(0, 0, 1, 1), ground_wgs=lambda x, y: (x, y))
            refs = [{'poly': box(x, 0, x+20, 20), 'component': 0,
                     'meta': {'id': str(x), 'height_m': 150, 'field': 'height'}} for x in (0, 50)]
            with patch.object(local, 'raw', return_value='fixture'), patch.object(overture_ghsl, 'first_epoch', return_value=[1980, None]) as sample:
                added, meta, report = gap_buildings([], refs, f, {})
            self.assertEqual(added[0][1:4], (150, 1980, 'epoch'))
            self.assertTrue(meta[0]['age_estimated'])
            self.assertEqual(meta[0]['age_resolution_m'], 100)
            self.assertEqual(report['counts']['no_ghsl_epoch'], 1)
            sample.assert_called_once_with('fixture', [(10, 10), (60, 10)], f.area, 1500)
    result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not result.wasSuccessful(): raise SystemExit(1)


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if sys.argv[1:] == ['selftest']: selftest()
    elif len(sys.argv) == 3 and sys.argv[1] == 'inspect':
        inspect(sys.argv[2])
    else: raise SystemExit(__doc__)
