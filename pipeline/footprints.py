"""Optional present-day appearance outlines. The prepared model, dates and statistics are never modified.

prep.py calls write after its normal outputs; `prep.py CITY --footprints-only` rebuilds this sidecar from an existing model.
Fetch the building_footprints theme explicitly first. `python -I pipeline/footprints.py selftest` tests the geometry policy.
"""
import array, collections, hashlib, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from shapely import hausdorff_distance
from shapely.affinity import scale as scale_shape, translate
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

import heights, layout, osm, osmgeo
from geo import Frame

DEFAULTS = {'enabled': False, 'source': 'primary', 'regularize': 'off', 'split_coverage': .4,
            'split_distribution': .7, 'child_coverage': .7, 'simplify_m': 2., 'angle_deg': 10.,
            'max_move_m': 1., 'max_area_change': .03}


def settings(value):
    value = value or {}
    if not isinstance(value,dict):raise ValueError('today_footprints: mapping required')
    unknown = set(value) - set(DEFAULTS)
    if unknown: raise ValueError(f'today_footprints: unknown keys {sorted(unknown)}')
    s = {**DEFAULTS, **value}
    if not isinstance(s['enabled'], bool): raise ValueError('today_footprints.enabled: boolean required')
    if s['source'] not in ('primary', 'osm_matched') or s['regularize'] not in ('off', 'guarded'):
        raise ValueError('today_footprints: source primary|osm_matched; regularize off|guarded')
    for k, lo, hi in [('split_coverage', .1, 1), ('split_distribution', .1, 1), ('child_coverage', .7, 1),
                      ('simplify_m', 0, 2), ('angle_deg', 0, 15), ('max_move_m', 0, 2), ('max_area_change', 0, .1)]:
        if isinstance(s[k], bool) or not isinstance(s[k], (int, float)) or not math.isfinite(s[k]) or not lo <= s[k] <= hi:
            raise ValueError(f'today_footprints.{k}: {lo}..{hi}')
    return s


def fingerprint(model):
    """SHA256 of a little-endian Float64 stream, shared with studio.js; no JSON number-format differences."""
    a = array.array('d', [1, model['scale'], model.get('bex', 1), len(model['b']), len(model['p']), *model['box']])
    for b in model['b']: a.extend(b[:2])
    for bi, h, rings, *tail in model['p']:
        a.extend([bi, h, tail[0] if tail else 0, len(rings)])
        for ring in rings:
            a.append(len(ring))
            for p in ring: a.extend(p[:2])
    if sys.byteorder != 'little': a.byteswap()
    return hashlib.sha256(a.tobytes()).hexdigest()


def polygons(model):
    s = model['scale']
    return [Polygon([(x/s, -z/s) for x,z in r[2][0]],
                    [[(x/s, -z/s) for x,z in h] for h in r[2][1:]]) for r in model['p']]


def references(city, frame, excluded=()):
    path = osm.cache_path(layout.raw(city), frame.area, 'building_footprints')
    if not os.path.isfile(path): raise ValueError(f'no whole-building cache; run pipeline/osm.py {city} building_footprints')
    data = json.load(open(path, encoding='utf-8')); refs = []; skipped = collections.Counter(); seen = {}
    for e in sorted(data['elements'], key=lambda e: e['type'] != 'relation'):
        tags = e.get('tags', {}); bid = f'{e["type"]}/{e["id"]}'
        if not tags.get('building') or tags['building'] in ('no', 'construction', 'proposed', 'demolished', 'ruins'):
            skipped['not_existing'] += 1; continue
        if tags.get('building:part', 'no') != 'no': skipped['part'] += 1; continue
        parts=osmgeo.polys(e,frame.to_utm.transform,repair=False)
        if not parts:skipped['invalid_or_unclosed']+=1
        for component, p in enumerate(parts):
            if p.geom_type != 'Polygon' or not p.is_valid or p.is_empty or p.area <= 0:
                skipped['invalid'] += 1; continue
            p = translate(p, -frame.cx, -frame.cy); key = p.normalize().wkb
            if key in seen:
                original=refs[seen[key]];original['excluded'] |= bid in excluded;original['aliases'].append(bid)
                skipped['duplicate'] += 1; continue
            seen[key]=len(refs)
            refs.append({'poly': p, 'id': bid, 'component': component, 'tags': tags, 'excluded': bid in excluded,
                         'url': f'https://www.openstreetmap.org/{bid}', 'aliases':[bid]})
    return refs, {'source': 'OpenStreetMap', 'licence': 'ODbL-1.0', 'cache': os.path.basename(path),
                  'snapshot': data.get('osm3s', {}).get('timestamp_osm_base'), 'skipped': dict(skipped)}


def orthogonal(p, angle=10):
    """Least vertex movement under near-axis constraints; diagonal edges and all rings remain."""
    rings = [np.asarray(r.coords[:-1], float) for r in [p.exterior, *p.interiors]]
    edges = [np.roll(r, -1, axis=0)-r for r in rings]; e = np.concatenate(edges)
    lengths = np.linalg.norm(e, axis=1); angles = np.arctan2(e[:,1], e[:,0])
    theta = np.angle(np.sum(lengths*np.exp(4j*angles)))/4
    c,s = math.cos(theta), math.sin(theta); R = np.array([[c,s],[-s,c]]); origin = np.array(p.centroid.coords[0])
    result = []
    for ring in rings:
        v = (ring-origin) @ R.T; n = len(v); ed = np.roll(v,-1,axis=0)-v
        a = np.abs((np.arctan2(ed[:,1],ed[:,0])+math.pi/2)%math.pi-math.pi/2)
        out = v.copy()
        for axis, near in [(0, np.abs(a-math.pi/2)<=math.radians(angle)), (1, a<=math.radians(angle))]:
            parent = list(range(n))
            def find(i):
                while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
                return i
            for i, yes in enumerate(near):
                if yes: parent[find(i)] = find((i+1)%n)
            groups = collections.defaultdict(list)
            for i in range(n): groups[find(i)].append(i)
            for group in groups.values(): out[group,axis] = v[group,axis].mean()
        result.append(out @ R + origin)
    return Polygon(result[0], result[1:])


def guarded(p, s):
    """Two-metre topology-preserving simplification, then a separately bounded near-axis adjustment."""
    def good(q, base, move):
        return (not q.is_empty and q.is_valid and q.geom_type == 'Polygon' and len(q.interiors)==len(p.interiors)
                and abs(q.area/base.area-1)<=s['max_area_change']
                and hausdorff_distance(base.boundary,q.boundary,densify=.1)<=move+1e-7)
    q = p.simplify(s['simplify_m'], preserve_topology=True)
    if not good(q,p,s['simplify_m']): q = p
    r = orthogonal(q,s['angle_deg'])
    if good(r,q,s['max_move_m']) and good(r,p,s['simplify_m']+s['max_move_m']): q = r
    return q


def create(model, refs, config, *, protected=(), seat=None):
    s = settings(config)
    if not s['enabled']: return {'version': 1, 'enabled': False}
    polys = polygons(model); tree = STRtree(polys); n = len(polys); protected = set(protected)
    counts = collections.Counter(); rejected = collections.Counter(); associations = collections.defaultdict(list)
    candidate_types = collections.defaultdict(set); geometry_hits = {}; reserved = set(); proposals = {}
    # Excluded named landmarks retain their base; still count as mapped for regularization eligibility.
    for ri,r in enumerate(refs):
        q = r['poly']; hits = heights.match_candidates(q,polys,tree); geometry_hits[ri] = hits
        if r.get('excluded'):
            for i in tree.query(q,predicate='intersects'):
                p=polys[int(i)]
                if p.intersection(q).area/min(p.area,q.area)>=.7 and p.buffer(3).covers(q.centroid):protected.add(int(i))
            continue
        contained = []
        for i in tree.query(q,predicate='intersects'):
            i=int(i);p=polys[i];cover=p.intersection(q).area/q.area
            if i not in protected and cover>=s['child_coverage'] and p.buffer(3).covers(q.centroid):
                contained.append((cover,i))
        contained.sort(reverse=True)
        if contained and (len(contained)==1 or contained[0][0]-contained[1][0]>=.05):
            associations[contained[0][1]].append(ri)
    blocked=set()
    if s['source']=='osm_matched':
        for i,ris in associations.items():
            if i in protected:continue
            if len(ris)<2: continue
            blocked.add(i);reserved.update(ris);candidate_types[i].add('osm_split')
            parts=[refs[k]['poly'] for k in ris];u=unary_union(parts);p=polys[i]
            coverage=u.intersection(p).area/p.area;distribution=u.convex_hull.intersection(p).area/p.area
            if sum(q.area for q in parts)-u.area>.01: rejected['split_children_overlap']+=1;continue
            if coverage<s['split_coverage']:rejected['split_coverage']+=1;continue
            if distribution<s['split_distribution']:rejected['split_distribution']+=1;continue
            proposals[i]={'source':'osm_split','parts':parts,'refs':ris,'coverage':coverage,'distribution':distribution}
        singles=collections.defaultdict(list)
        for ri,hits in geometry_hits.items():
            if ri in reserved or refs[ri].get('excluded') or not hits:continue
            if len(hits)>1 and hits[0][0]-hits[1][0]<.05:rejected['ambiguous_reference']+=1;continue
            score,i=hits[0]
            if i in protected or i in blocked:continue
            candidate_types[i].add('osm_single');singles[i].append((score,ri))
        for i,options in singles.items():
            if len(options)!=1:rejected['multiple_single_references']+=1;continue
            score,ri=options[0]
            proposals[i]={'source':'osm_single','parts':[refs[ri]['poly']],'refs':[ri],'iou':score}
    if s['regularize']=='guarded':
        ot=STRtree([r['poly'] for r in refs])
        for i,p in enumerate(polys):
            if i in protected or not p.is_valid or p.is_empty:continue
            if sum(p.intersection(refs[k]['poly']).area for k in ot.query(p,predicate='intersects'))>1:continue
            candidate_types[i].add('regularized');q=guarded(p,s)
            if not p.equals_exact(q,1e-7):proposals[i]={'source':'regularized','parts':[q],'refs':[]}
    # Quantize exactly as the prepared outlines; assess collisions on what the renderer will actually use.
    S=model['scale']
    def rings(q):return [[[round(x*S,5),round(-y*S,5)] for x,y in r.coords[:-1]] for r in [q.exterior,*q.interiors]]
    for i in list(proposals):
        item=proposals[i];item['rings']=[rings(q) for q in item['parts']]
        item['parts']=[Polygon([(x/S,-z/S) for x,z in rr[0]], [[(x/S,-z/S) for x,z in h] for h in rr[1:]]) for rr in item['rings']]
        if any(not q.is_valid or q.is_empty for q in item['parts']):rejected['quantized_invalid']+=1;del proposals[i];continue
        p=polys[i];u=unary_union(item['parts'])
        if item['source']=='osm_split':
            coverage=u.intersection(p).area/p.area;distribution=u.convex_hull.intersection(p).area/p.area
            if (any(p.intersection(q).area/q.area<s['child_coverage'] for q in item['parts'])
                or coverage<s['split_coverage'] or distribution<s['split_distribution']
                or sum(q.area for q in item['parts'])-u.area>.01):
                rejected['quantized_split_guard']+=1;del proposals[i];continue
            item.update(coverage=coverage,distribution=distribution)
        elif item['source']=='regularized':
            if (len(item['parts'][0].interiors)!=len(p.interiors) or abs(u.area/p.area-1)>s['max_area_change']
                or hausdorff_distance(p.boundary,u.boundary,densify=.1)>s['simplify_m']+s['max_move_m']+1e-7):
                rejected['quantized_regularization_guard']+=1;del proposals[i];continue
        else:
            hits=heights.match_candidates(item['parts'][0],polys,tree)
            if not hits or hits[0][1]!=i or len(hits)>1 and hits[0][0]-hits[1][0]<.05:
                rejected['quantized_single_guard']+=1;del proposals[i];continue
        if len(item['parts'])==1 and polys[i].equals_exact(item['parts'][0],1e-7):del proposals[i]
    # Reject conflicts simultaneously; rollbacks can expose an old outline, so repeat until the remaining choices are stable.
    while proposals:
        effective=[unary_union(proposals[i]['parts']) if i in proposals else p for i,p in enumerate(polys)]
        et=STRtree(effective);bad=set()
        for i in proposals:
            for j in et.query(effective[i],predicate='intersects'):
                j=int(j)
                if j==i:continue
                if effective[i].intersection(effective[j]).area>polys[i].intersection(polys[j]).area+.01:
                    bad.add(i)
                    if j in proposals:bad.add(j)
        if not bad:break
        for i in bad:del proposals[i];rejected['new_overlap']+=1
    output=[]
    for i,item in sorted(proposals.items()):
        bi,oldh,_,oldbase=model['p'][i];approved=model['b'][bi][1];children=[]
        for k,(q,rr) in enumerate(zip(item['parts'],item['rings'])):
            height=approved;meta={'source':'primary approved height','height_m':approved,'estimated':True}
            if item['refs']:
                ref=refs[item['refs'][k]];got=heights.height(ref.get('tags',{}))
                if got and got[1]=='height' and not got[3] and got[0]>height:
                    height=got[0];meta={'source':'OSM height','height_m':height,'estimated':False,'value':got[2]}
                meta.update(osm_id=ref['id'],component=ref.get('component',0),url=ref.get('url'))
            h,base=seat(rr,height) if seat else (oldh+(height-approved)*S*model.get('bex',1),oldbase)
            children.append({'rings':rr,'h':round(h,7),'base':round(base,7),'height_m':height,'height_source':meta})
        output.append({'pi':i,'bi':bi,'source':item['source'],'children':children,
                       **{k:round(item[k],6) for k in ('coverage','distribution','iou') if k in item}})
        counts[item['source']]+=1;counts['children']+=len(children)
    for kind in ('osm_single','osm_split','regularized'):
        counts['candidate_'+kind]=sum(kind in kinds for kinds in candidate_types.values())
    counts['candidate_primaries']=len(candidate_types);counts['replaced_primaries']=len(output)
    counts['primary_count']=n;counts['protected']=len(protected)
    return {'version':1,'enabled':True,'model_fingerprint':fingerprint(model),'parameters':s,
            'counts':dict(counts),'rejected':dict(rejected),'replacements':output,
            'candidates':[{'pi':i,'bi':model['p'][i][0],'types':sorted(kinds)} for i,kinds in sorted(candidate_types.items())]}


def write(city, city_config=None):
    import yaml,terrainio
    C=city_config or yaml.safe_load(open(os.path.join(city,'city.yaml'),encoding='utf-8'))
    s=settings(C.get('buildings',{}).get('today_footprints'));out=layout.data(city,'today_footprints.json')
    if not s['enabled']:
        result={'version':1,'enabled':False}
    else:
        path=layout.data(city,'model.json');raw=open(path,'rb').read();M=json.loads(raw);F=Frame(M['box'],M['scale'])
        excluded=C.get('buildings',{}).get('height_supplement',{}).get('exclude_osm',[])
        refs,provenance=references(city,F,excluded) if s['source']=='osm_matched' or s['regularize']=='guarded' else ([],{'source':'primary'})
        protected=[]
        hp=layout.data(city,'building_heights.json')
        if os.path.isfile(hp):
            H=json.load(open(hp));added=H.get('fill_gaps',{}).get('counts',{}).get('added',0)
            sp=layout.data(city,'stats.json');extra=json.load(open(sp)).get('age_how',{}).get('fill',0) if os.path.isfile(sp) else 0
            protected=list(range(len(M['p'])-added-extra,len(M['p']))) if added+extra else []
        image,tj=terrainio.load(city) if M.get('terrain') else (None,None)
        plate=terrainio.plate_mesh(image,*M['size']) if image is not None else None
        def seat(rr,h):
            if plate is None:return h*M['scale']*M.get('bex',1),0
            ring=rr[0];centre=Polygon(ring,rr[1:]).centroid;cx,cz=centre.x,centre.y
            mid=plate(cx,cz)*M['scale']*M.get('terrain',{}).get('exaggeration',1)
            base=min(mid,plate.lowest(ring)*M['scale']*M.get('terrain',{}).get('exaggeration',1))
            return h*M['scale']*M.get('bex',1)+mid-base,base
        result=create(M,refs,s,protected=protected,seat=seat)
        result.update(model_sha256=hashlib.sha256(raw).hexdigest(),provenance=provenance)
    tmp=out+'.tmp';json.dump(result,open(tmp,'w',encoding='utf-8'),separators=(',',':'),ensure_ascii=False);os.replace(tmp,out)
    print('today_footprints: '+json.dumps(result.get('counts',{'enabled':False}),ensure_ascii=False))
    return result


def review(city, areas_file, out):
    """Before/after plan overlays and population coverage for named WGS84 study circles, from the actual sidecar."""
    import yaml,register
    from shapely.geometry import Point,box
    from PIL import Image,ImageDraw,ImageFont
    os.makedirs(out,exist_ok=True)
    M=json.load(open(layout.data(city,'model.json')));J=json.load(open(layout.data(city,'today_footprints.json')))
    if not J.get('enabled') or J['model_fingerprint']!=fingerprint(M):raise ValueError('review: enabled, current sidecar required')
    F=Frame(M['box'],M['scale']);P=polygons(M);reps={r['pi']:r for r in J['replacements']};candidates={r['pi']:r['types'] for r in J['candidates']}
    H=json.load(open(layout.data(city,'building_heights.json')));stats=json.load(open(layout.data(city,'stats.json')))
    n=len(P)-H.get('fill_gaps',{}).get('counts',{}).get('added',0)-stats.get('age_how',{}).get('fill',0)
    report={'provenance':J['provenance'],'counts':J['counts'],'regions':{}}
    font=lambda size:ImageFont.load_default(size=size)
    register.COLOURS.update(original=(255,145,63),replacement=(76,231,158),unchanged=(91,110,130))
    def model_poly(rr):return Polygon([(x/M['scale'],-z/M['scale']) for x,z in rr[0]], [[(x/M['scale'],-z/M['scale']) for x,z in h] for h in rr[1:]])
    for area in yaml.safe_load(open(areas_file,encoding='utf-8'))['areas']:
        x,y=F.to_utm.transform(*area['ll']);x-=F.cx;y-=F.cy;radius=area['radius_m'];c=Point(x,y)
        ix=[i for i,p in enumerate(P[:n]) if p.centroid.distance(c)<=radius];accepted=[i for i in ix if i in reps];candidate=[i for i in ix if i in candidates]
        total=sum(P[i].area for i in ix)
        region={'primary_n':len(ix),'area_m2':total,'candidate_n':len(candidate),'actual_n':len(accepted),
                'candidate_count_pct':100*len(candidate)/len(ix),'candidate_area_pct':100*sum(P[i].area for i in candidate)/total,
                'actual_count_pct':100*len(accepted)/len(ix),'actual_area_pct':100*sum(P[i].area for i in accepted)/total,
                'types':dict(collections.Counter(reps[i]['source'] for i in accepted)),
                'children':sum(len(reps[i]['children']) for i in accepted)}
        report['regions'][area['id']]=region
        for mode in ('area','detail'):
            centre=(x,y);span=radius*1.06
            if mode=='detail':
                i=next(i for i,r in enumerate(M['p']) if r[0]==area['focus_bi']);p=P[i];centre=p.centroid.coords[0]
                span=max(130,max(p.bounds[2]-p.bounds[0],p.bounds[3]-p.bounds[1])*.85)
            cx,cy=centre;W,HH=1500,1650;src=register.Source.scaled(F,(750,840),F.to_wgs.transform(F.cx+cx,F.cy+cy),2*span/1340)
            im=Image.new('RGB',(W,HH),(22,30,42));d=ImageDraw.Draw(im)
            d.text((35,20),area['id'].upper()+' / '+mode.upper(),font=font(34),fill='white')
            d.text((35,68),'Original: orange   Actual appearance: green   Retained: grey',font=font(23),fill='white')
            d.text((35,110),f'Candidates {len(candidate)}/{len(ix)}; actual {len(accepted)} ({region["actual_count_pct"]:.1f}% count / {region["actual_area_pct"]:.1f}% area)',font=font(22),fill='white')
            d.rectangle((80,170,1420,1510),outline=(90,110,130),width=2)
            d.text((35,1540),'OSM snapshot '+str(J['provenance'].get('snapshot'))+' | CMAB years and parent identity retained',font=font(20),fill='white')
            d.text((35,1580),'Children share their parent year, growth and hide centre. Regularized outlines are schematic.',font=font(20),fill='white')
            base=os.path.join(out,area['id']+'_'+mode+'_base.png');im.save(base);features=[];window=box(cx-span,cy-span,cx+span,cy+span)
            def add(p,kind):
                if not p.intersects(window):return
                for q in getattr(p.intersection(window),'geoms',[p.intersection(window)]):
                    if q.geom_type!='Polygon':continue
                    for ring in [q.exterior,*q.interiors]:
                        features.append({'type':'Feature','properties':{'kind':kind},'geometry':{'type':'LineString','coordinates':[F.to_wgs.transform(F.cx+a,F.cy+b) for a,b in ring.coords]}})
            for i,p in enumerate(P):
                if not p.intersects(window):continue
                add(p,'original' if i in reps else 'unchanged')
            for i,r in reps.items():
                if not P[i].intersects(window):continue
                for child in r['children']:add(model_poly(child['rings']),'replacement')
            target=os.path.join(out,area['id']+'_'+mode+'.png');register.overlay(base,src,{'features':features},target)
        print(area['id']+': '+json.dumps(region,ensure_ascii=False))
    json.dump(report,open(os.path.join(out,'coverage.json'),'w'),indent=1,ensure_ascii=False)
    return report


def selftest():
    import unittest
    from shapely.geometry import box
    class Tests(unittest.TestCase):
        def model(self,ps):return {'scale':.001,'bex':1,'box':[0,0,1,1],'b':[[1985,12] for p in ps],
            'p':[[i,.012,[[[x*.001,-y*.001] for x,y in p.exterior.coords[:-1]]],0] for i,p in enumerate(ps)]}
        def ref(self,p,n=1,**tags):return {'poly':p,'id':f'way/{n}','component':0,'tags':tags}
        def test_disabled(self):self.assertEqual(create({},[],{}),{'version':1,'enabled':False})
        def test_appearance_fetch_is_explicit(self):self.assertNotIn('building_footprints',osm.DEFAULT_THEMES)
        def test_split_inherits_without_mutating(self):
            m=self.model([box(0,0,100,50)]);before=json.dumps(m);rr=[self.ref(box(2,2,42,48),1,height='30'),self.ref(box(58,2,98,48),2)]
            r=create(m,rr,{'enabled':True,'source':'osm_matched'})
            self.assertEqual(r['counts']['osm_split'],1);self.assertEqual(len(r['replacements'][0]['children']),2)
            self.assertEqual([c['height_m'] for c in r['replacements'][0]['children']],[30,12]);self.assertEqual(json.dumps(m),before)
        def test_sparse_or_overlapping_split_refused(self):
            m=self.model([box(0,0,100,100)])
            for rr in ([self.ref(box(0,0,10,10)),self.ref(box(90,90,100,100),2)],
                       [self.ref(box(0,0,80,100)),self.ref(box(20,0,100,100),2)]):
                self.assertFalse(create(m,rr,{'enabled':True,'source':'osm_matched'})['replacements'])
        def test_distribution_guard_and_protected_parent(self):
            m=self.model([box(0,0,100,100)])
            rr=[self.ref(box(0,0,20,100)),self.ref(box(25,0,45,100),2)]
            r=create(m,rr,{'enabled':True,'source':'osm_matched'})
            self.assertFalse(r['replacements']);self.assertEqual(r['rejected']['split_distribution'],1)
            rr=[self.ref(box(0,0,45,100)),self.ref(box(55,0,100,100),2)]
            self.assertFalse(create(m,rr,{'enabled':True,'source':'osm_matched'},protected=[0])['replacements'])
        def test_new_neighbor_overlap_refused(self):
            m=self.model([box(0,0,20,20),box(21,0,40,20)])
            r=create(m,[self.ref(box(0,0,23,20))],{'enabled':True,'source':'osm_matched'})
            self.assertFalse(r['replacements']);self.assertGreater(r['rejected']['new_overlap'],0)
        def test_ambiguous_reference_and_parts_not_regularized(self):
            m=self.model([box(0,0,20,20),box(0,0,20,20)])
            self.assertFalse(create(m,[self.ref(box(0,0,20,20))],{'enabled':True,'source':'osm_matched'})['replacements'])
        def test_guard_keeps_diagonal_and_holes(self):
            p=Polygon([(0,0),(20,.2),(20,20),(3,20),(0,17)])
            q=guarded(p,settings({'regularize':'guarded'}));self.assertTrue(q.is_valid)
            self.assertLessEqual(hausdorff_distance(p.boundary,q.boundary,densify=.1),3.000001)
            self.assertLessEqual(abs(q.area/p.area-1),.030001)
        def test_lower_or_estimated_heights_do_not_override(self):
            m=self.model([box(0,0,20,20)])
            for tags in ({'height':'8'},{'height':'50','source:height':'estimated'},{'building:levels':'30'}):
                r=create(m,[self.ref(box(0,0,19,20),**tags)],{'enabled':True,'source':'osm_matched'})
                self.assertEqual(r['replacements'][0]['children'][0]['height_m'],12)
        def test_cross_language_fingerprint(self):
            m={'scale':.001,'box':[0,0,1,1],'bex':1,'b':[[1985,12]],'p':[[0,.012,[[[0,0],[.02,0],[.02,.02],[0,.02]]],0]]}
            self.assertEqual(fingerprint(m),'2e4e17dbc807c2b99526e5fc1adf301242da6ab7f88572c5be6a0ddecb38cc58')
        def test_all_outlines_read_without_height_but_parts_excluded(self):
            import tempfile
            from unittest.mock import patch
            with tempfile.TemporaryDirectory() as d:
                f=os.path.join(d,'answer.json');g=[{'lon':0,'lat':0},{'lon':.001,'lat':0},{'lon':.001,'lat':.001},{'lon':0,'lat':0}]
                crossed=[g[0],g[2],g[1],{'lon':0,'lat':.001},g[0]]
                els=[{'type':'way','id':1,'tags':{'building':'yes'},'geometry':g},
                     {'type':'way','id':2,'tags':{'building':'yes','building:part':'yes'},'geometry':g},
                     {'type':'way','id':3,'tags':{'building':'yes'},'geometry':crossed}]
                json.dump({'elements':els},open(f,'w'))
                with patch.object(osm,'cache_path',return_value=f):rr,meta=references(d,Frame([0,0,.01,.01],.001))
                self.assertEqual(len(rr),1);self.assertEqual(meta['skipped']['part'],1);self.assertEqual(meta['skipped']['invalid'],1)
        def test_disabled_writer_and_optional_web_packing(self):
            import tempfile,importlib.util
            spec=importlib.util.spec_from_file_location('footprint_web',os.path.join(os.path.dirname(__file__),'..','tools','web.py'))
            web=importlib.util.module_from_spec(spec);spec.loader.exec_module(web)
            with tempfile.TemporaryDirectory() as d:
                os.makedirs(layout.data(d));json.dump({},open(layout.build(d,'film.json'),'w'))
                target=layout.data(d,'today_footprints.json');json.dump({'enabled':True},open(target,'w'))
                self.assertIn('build/data/today_footprints.json',web.files(d))
                write(d,{'buildings':{}})
                self.assertFalse(json.load(open(target))['enabled'])
                self.assertNotIn('build/data/today_footprints.json',web.files(d))
        def test_duplicate_alias_preserves_exclusion(self):
            import tempfile
            from unittest.mock import patch
            g=[{'lon':0,'lat':0},{'lon':.001,'lat':0},{'lon':.001,'lat':.001},{'lon':0,'lat':0}]
            els=[{'type':'way','id':1,'tags':{'building':'yes'},'geometry':g},
                 {'type':'relation','id':2,'tags':{'building':'yes','type':'multipolygon'},'members':[{'type':'way','role':'outer','geometry':g}]}]
            with tempfile.TemporaryDirectory() as d:
                f=os.path.join(d,'answer.json');json.dump({'elements':els},open(f,'w'))
                with patch.object(osm,'cache_path',return_value=f):rr,_=references(d,Frame([0,0,.01,.01],.001),['way/1'])
                self.assertEqual(len(rr),1);self.assertTrue(rr[0]['excluded']);self.assertIn('way/1',rr[0]['aliases'])
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not r.wasSuccessful():raise SystemExit(1)


if __name__=='__main__':
    if sys.argv[1:]==['selftest']:selftest()
    elif len(sys.argv)==5 and sys.argv[1]=='review':review(*sys.argv[2:])
    else:raise SystemExit(__doc__+'\nReview: pipeline/footprints.py review CITY AREAS.yaml OUT_FOLDER')
