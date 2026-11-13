"""Supplement a building adapter's low heights with spatially matched public OSM building heights.

The primary footprint, order, year, age method and function are preserved. One mapped whole building can raise at most one
primary footprint; roof / antenna / other building parts are not whole-building height references. Explicit height beats a
storey estimate. A missing, ambiguous, distant or lower reference leaves the primary height unchanged. No network in prep:
fetch the area's building_heights theme with pipeline/osm.py first (docs/DATA.md).

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


def height(tags, floor_height_m=3.2):
    """A height tag is the top above ground, not an addition to min_height. Storeys remain an estimate."""
    h = metres(tags.get('height'))
    if h is not None: return h, 'height', tags['height'], 'estimat' in tags.get('source:height', '').lower()
    levels = str(tags.get('building:levels', '')).strip()
    if re.fullmatch(r'\d+(?:\.0+)?', levels) and 0 < float(levels) <= 300:
        return float(levels) * floor_height_m, 'building:levels', tags['building:levels'], True
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


def supplement(buildings, refs):
    """Return the same adapter records with raised heights and indexed provenance, plus matching counts.

    Match a reference's centre to a containing primary polygon (3m mapping tolerance), with >=70% overlap of the smaller
    footprint, >=1/4 area ratio and >=35% IoU. The strongest overlap wins; nearly tied overlaps or conflicting nearly tied
    whole-building references are refused. There is no nearest-building fallback across a street or onto a podium.
    """
    rows = list(buildings); polys = [b[0] for b in rows]; tree = STRtree(polys)
    candidates = collections.defaultdict(list); counts = collections.Counter(); unmatched = []
    for r in refs:
        q = r['poly']; hits = []
        for i in tree.query(q, predicate='intersects'):
            i = int(i); p = polys[i]
            if not p.buffer(3).covers(q.centroid): continue
            area = p.intersection(q).area
            cover = area / min(p.area, q.area); ratio = min(p.area, q.area) / max(p.area, q.area)
            iou = area / (p.area + q.area - area)
            if cover >= .7 and ratio >= .25 and iou >= .35: hits.append((iou, i))
        hits.sort(reverse=True)
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
        if m['height_m'] <= old: counts['primary_kept'] += 1; continue
        selected[i] = {**m, 'primary_height_m': old, 'match_iou': round(score, 4)}
        p, _, year, how, func = rows[i]
        rows[i] = p, m['height_m'], year, how, func
        changes.append({'bi': i, **selected[i]}); counts['raised'] += 1; counts[m['source']] += 1
    return rows, selected, {'counts': dict(counts), 'changes': changes,
                            'unmatched_tall': sorted(unmatched, key=lambda x: -x['height_m'])}


def load(city, frame, buildings, settings):
    """The opt-in prep adapter. New cities use configuration, never a city name or tower-specific code."""
    if settings.get('source', 'osm') != 'osm': raise SystemExit('heights: height_supplement.source must be osm')
    floor = float(settings.get('floor_height_m', 3.2))
    if not math.isfinite(floor) or not 2 <= floor <= 6: raise SystemExit('heights: floor_height_m must be between 2 and 6 metres')
    refs, provenance = references(city, frame, floor)
    excluded = set(settings.get('exclude_osm', []))
    if excluded:
        refs = [r for r in refs if r['meta']['id'] not in excluded]
        provenance['excluded_osm'] = sorted(excluded)
    rows, selected, result = supplement(buildings, refs)
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
