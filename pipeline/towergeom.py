"""Shared metre geometry for high-rise landmarks and detailed Blender models.

Coordinates are x east, y north, z up about the landmark's axis. No city names, bpy, NumPy or GIS dependencies: the film
adapter and the Blender kinds read the same outlines, sections, spheres and members. Sizes are source data, not defaults.
Run `uv run python -I pipeline/towergeom.py selftest` for geometry and aperture regression checks.
"""
import bisect, copy, math, sys


def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def area(p): return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2


def triangles(poly):
    """Ear clipping of a simple planar outline, including a concave facade recess; retain original boundary indices."""
    live = list(range(len(poly))); out = []
    turn = lambda a,b,c: (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    if area(poly) < 0: live.reverse()
    while len(live) > 3:
        for j, b in enumerate(live):
            a, c = live[j-1], live[(j+1)%len(live)]
            if turn(poly[a],poly[b],poly[c]) <= 1e-10: continue
            if any(all(turn(poly[u],poly[v],poly[k]) >= -1e-10 for u,v in ((a,b),(b,c),(c,a)))
                   for k in live if k not in (a,b,c)): continue
            out.append((a,b,c)); live.pop(j); break
        else:
            # Collinear boundary points still belong to the side surface. A fan keeps their zero-area cap triangles,
            # which finish() drops; exact duplicate points are refused in the source outline.
            out += [(live[0],live[j],live[j+1]) for j in range(1,len(live)-1)]; return out
    out.append(tuple(live)); return out


class Mesh:
    def __init__(self, name, material='stone', smooth=True):
        self.name, self.material, self.smooth = name, material, smooth; self.v=[]; self.f=[]
    def vertex(self, p): self.v.append(tuple(p)); return len(self.v)-1
    def face(self, *q):
        for j in range(1,len(q)-1):
            a,b,c = q[0],q[j],q[j+1]
            if math.dist(cross(sub(self.v[b],self.v[a]),sub(self.v[c],self.v[a])),(0,0,0)) > 1e-10:
                self.f.append((a,b,c))
    def finish(self): return {'name':self.name,'material':self.material,'smooth':self.smooth,'v':self.v,'f':self.f}


def resample(p, n):
    lengths=[0.0]
    for a,b in zip(p,p[1:]+p[:1]): lengths.append(lengths[-1]+math.dist(a,b))
    out=[]
    for j in range(n):
        d=j/n*lengths[-1]; k=min(len(p)-1,bisect.bisect_right(lengths,d)-1)
        f=(d-lengths[k])/max(lengths[k+1]-lengths[k],1e-12)
        out.append(tuple(p[k][i]*(1-f)+p[(k+1)%len(p)][i]*f for i in range(2)))
    return out


def loft(name, rings, material='glass', smooth=True):
    """Closed ruled loft; rings are (x,y,z), ordered counter-clockwise seen from above."""
    n=max(len(r) for r in rings)
    if any(len(r)!=n for r in rings):
        n=max(32,n); rings=[[(x,y,r[0][2]) for x,y in resample([(x,y) for x,y,_ in r],n)] for r in rings]
    m=Mesh(name,material,smooth); shared={}
    def vertex(p):
        key=tuple(round(v,9) for v in p)
        if key not in shared:shared[key]=m.vertex(p)
        return shared[key]
    ids=[[vertex(p) for p in r] for r in rings]
    for lo,hi in zip(ids,ids[1:]):
        for i in range(n): m.face(lo[i],lo[(i+1)%n],hi[(i+1)%n],hi[i])
    for a,b,c in triangles([(x,y) for x,y,_ in rings[0]]): m.face(ids[0][c],ids[0][b],ids[0][a])
    for a,b,c in triangles([(x,y) for x,y,_ in rings[-1]]): m.face(ids[-1][a],ids[-1][b],ids[-1][c])
    return m.finish()


def rod(name, a, b, radius, radius1=None, sides=12, material='stone'):
    d=sub(b,a); length=math.dist(a,b)
    if length <= 1e-8: raise ValueError('member endpoints must differ')
    axis=tuple(q/length for q in d); u=cross(axis,(0,0,1) if abs(axis[2])<.9 else (1,0,0))
    norm=math.dist(u,(0,0,0)); u=tuple(q/norm for q in u); v=cross(axis,u)
    m=Mesh(name,material); rings=[]
    for p,r in ((a,radius),(b,radius if radius1 is None else radius1)):
        rings.append([m.vertex(tuple(p[k]+r*(u[k]*math.cos(i/sides*math.tau)+v[k]*math.sin(i/sides*math.tau)) for k in range(3))) for i in range(sides)])
    ca,cb=m.vertex(a),m.vertex(b)
    for i in range(sides):
        j=(i+1)%sides; m.face(rings[0][i],rings[0][j],rings[1][j],rings[1][i])
        m.face(ca,rings[0][j],rings[0][i]);m.face(cb,rings[1][i],rings[1][j])
    return m.finish()


def sphere(name, at, diameter, sides=32, rows=16):
    m=Mesh(name); r=diameter/2; x,y,z=at
    pole0=m.vertex((x,y,z-r)); rings=[]
    for j in range(1,rows):
        a=-math.pi/2+j/rows*math.pi; rr=r*math.cos(a)
        rings.append([m.vertex((x+rr*math.cos(i/sides*math.tau),y+rr*math.sin(i/sides*math.tau),z+r*math.sin(a))) for i in range(sides)])
    pole1=m.vertex((x,y,z+r))
    for i in range(sides):
        j=(i+1)%sides; m.face(pole0,rings[0][j],rings[0][i]);m.face(pole1,rings[-1][i],rings[-1][j])
    for a,b in zip(rings,rings[1:]):
        for i in range(sides): j=(i+1)%sides;m.face(a[i],a[j],b[j],b[i])
    return m.finish()


def panel(name, points, thickness):
    """A convex planar crown fin or facade plate, with two real sides and closed edges."""
    normal=cross(sub(points[1],points[0]),sub(points[2],points[0]));length=math.dist(normal,(0,0,0))
    if length<1e-8:raise ValueError('panel needs three noncollinear points')
    normal=tuple(v/length for v in normal)
    if any(abs(sum(a*b for a,b in zip(sub(p,points[0]),normal)))>1e-3 for p in points):raise ValueError('panel points must be planar')
    m=Mesh(name,'metal',False);n=len(points)
    ids=[[m.vertex(tuple(p[i]+sign*normal[i]*thickness/2 for i in range(3))) for p in points] for sign in (-1,1)]
    for j in range(1,n-1):m.face(ids[0][0],ids[0][j+1],ids[0][j]);m.face(ids[1][0],ids[1][j],ids[1][j+1])
    for j in range(n):k=(j+1)%n;m.face(ids[0][j],ids[0][k],ids[1][k],ids[1][j])
    return m.finish()


def clip(poly, axis, bound, less=True):
    """Clip a plan by one half-plane (the two piers beside a through-opening)."""
    out=[]; inside=lambda p: p[axis]<=bound+1e-8 if less else p[axis]>=bound-1e-8
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ia,ib=inside(a),inside(b)
        if ia: out.append(a)
        if ia != ib:
            t=(bound-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(2)))
    return out


def section_at(S, z):
    rows=S['sections']; k=min(len(rows)-2,max(0,bisect.bisect_right([q['z_m'] for q in rows],z)-1))
    a,b=rows[k:k+2]; f=(z-a['z_m'])/max(b['z_m']-a['z_m'],1e-12)
    out={'z_m':z}
    for key,default in (('scale',[1,1]),('offset_m',[0,0])):
        av,bv=a.get(key,default),b.get(key,default);out[key]=[x*(1-f)+y*f for x,y in zip(av,bv)]
    out['turn_deg']=a.get('turn_deg',0)*(1-f)+b.get('turn_deg',0)*f
    pa,pb=a.get('plan_m',S['plan_m']),b.get('plan_m',S['plan_m'])
    if len(pa)!=len(pb): pa,pb=resample(pa,64),resample(pb,64)
    out['plan_m']=[[x*(1-f)+y*f for x,y in zip(p,q)] for p,q in zip(pa,pb)]
    return out


def plan(S, q):
    p=q.get('plan_m',S['plan_m']); sx,sy=q.get('scale',[1,1]); ox,oy=q.get('offset_m',[0,0]);a=math.radians(q.get('turn_deg',0));c,s=math.cos(a),math.sin(a)
    out=[(ox+x*sx*c-y*sy*s,oy+x*sx*s+y*sy*c) for x,y in p]
    return out if area(out)>0 else out[::-1]


def highrise(S, detailed=False):
    rows=[]
    for a,b in zip(S['sections'],S['sections'][1:]):
        rows.append(a)
        n=max(1,math.ceil(abs(b.get('turn_deg',0)-a.get('turn_deg',0))/4),math.ceil((b['z_m']-a['z_m'])/(12 if detailed else 24)))
        # The last ring is the sloped roof itself. An intermediate horizontal ring there would poke through its low side.
        if b['z_m']>a['z_m'] and not (S.get('crown_slope_m',0) and b['z_m']==S['h_m']):
            rows.extend(section_at(S,a['z_m']+(b['z_m']-a['z_m'])*j/n) for j in range(1,n))
    rows.append(S['sections'][-1]); opening=S.get('opening'); segments=[]
    if opening:
        z0,z1=opening['z0_m'],opening['z1_m']
        cuts=[S['sections'][0]['z_m'],z0,z1,S['h_m']]
        for j,(a,b) in enumerate(zip(cuts,cuts[1:])):
            r=[section_at(S,a)]+[q for q in rows if a<q['z_m']<b]+[section_at(S,b)]
            segments += [(f'body_{j}',r,None)] if j!=1 else [('opening_left',r,True),('opening_right',r,False)]
    else: segments=[('body',rows,None)]
    out=[]
    for name,qs,side in segments:
        rings=[]
        for q in qs:
            p=plan(S,q)
            if side is not None:
                f=(q['z_m']-opening['z0_m'])/(opening['z1_m']-opening['z0_m']);w=opening['w0_m']*(1-f)+opening['w1_m']*f
                p=clip(p,0,-w/2 if side else w/2,side)
            slope=S.get('crown_slope_m',0) if q['z_m']==S['h_m'] else 0
            direction=math.radians(S.get('crown_direction_deg',0)); proj=[x*math.cos(direction)+y*math.sin(direction) for x,y in p]
            low,high=min(proj),max(proj)
            rings.append([(x,y,q['z_m']-slope*(high-t)/max(high-low,1e-9)) for (x,y),t in zip(p,proj)])
        out.append(loft(name,rings))
        if detailed and S.get('facade'): out.extend(facade(S,name,qs,side))
    for i,p in enumerate(S.get('panels',[])):out.append(panel(p.get('id',f'crown_panel_{i}'),p['points_m'],p['thickness_m']))
    return out


def ring_band(name,p,z,height,width):
    """A closed narrow belt round any plan, independent of its height or region."""
    cx=sum(x for x,y in p)/len(p);cy=sum(y for x,y in p)/len(p)
    expanded=[]
    for x,y in p:
        d=max(math.hypot(x-cx,y-cy),1e-8);expanded.append((x+(x-cx)*width/d,y+(y-cy)*width/d))
    m=Mesh(name,'metal',False);n=len(p)
    rings=[[m.vertex((x,y,h)) for x,y in r] for r,h in ((p,z),(expanded,z),(expanded,z+height),(p,z+height))]
    for a,b in zip(rings,rings[1:]+rings[:1]):
        for i in range(n):j=(i+1)%n;m.face(a[i],a[j],b[j],b[i])
    return m.finish()


def facade(S,name,qs,side):
    F=S['facade'];out=[];z0=qs[0]['z_m'];z1=min(qs[-1]['z_m'],F.get('top_m',S['h_m']));step=F.get('floor_m',4);opening=S.get('opening')
    def outline(z):
        p=plan(S,section_at(S,z))
        if side is not None:
            f=(z-opening['z0_m'])/(opening['z1_m']-opening['z0_m']);w=opening['w0_m']*(1-f)+opening['w1_m']*f
            p=clip(p,0,-w/2 if side else w/2,side)
        return p
    for i in range(math.ceil(z0/step),math.floor((z1-S.get('crown_slope_m',0)-F.get('band_h_m',.35))/step)+1):
        z=i*step
        if z<=z0+.1:continue
        out.append(ring_band(f'{name}_belt_{i}',outline(z),z,F.get('band_h_m',.35),F.get('band_m',.3)))
    # Vertical mullions follow the ruled surface and stop at a through-opening's sill/head. No bars cross its void.
    for j,(a,b) in enumerate(zip(qs,qs[1:])):
        if a['z_m']>=z1:continue
        if b['z_m']>z1:b=section_at(S,z1)
        if b['z_m']-a['z_m']<.1:continue
        pa,pb=outline(a['z_m']),outline(b['z_m'])
        if len(pa)!=len(pb):continue
        for i,(u,v) in enumerate(zip(pa,pa[1:]+pa[:1])):
            n=max(1,math.ceil(math.dist(u,v)/F.get('bay_m',3)))
            for k in range(n):
                f=k/n; x,y=(u[t]*(1-f)+v[t]*f for t in range(2));u1,v1=pb[i],pb[(i+1)%len(pb)]
                x1,y1=(u1[t]*(1-f)+v1[t]*f for t in range(2))
                # The sloped crown is part of the body, not a rectangular curtain wall above it.
                if b['z_m']>S['h_m']-S.get('crown_slope_m',0):continue
                out.append(rod(f'{name}_mullion_{j}_{i}_{k}',(x,y,a['z_m']),(x1,y1,b['z_m']),F.get('mullion_m',.25)/2,sides=4,material='metal'))
    return out


def broadcast_tower(S,detailed=False):
    out=[]
    for i,s in enumerate(S['spheres']):
        x,y=s.get('at_m',[0,0]);z=s['z_m'];d=s['d_m'];name=s.get('id',f'sphere_{i}')
        out.append(sphere(name,(x,y,z),d,48 if detailed else 24,24 if detailed else 12))
        if detailed and s.get('band_share',.24)>0:
            # A thin equatorial glazing belt; its proportions, like the sphere's, are supplied by the city's sources.
            a=math.asin(s.get('band_share',.24));m=Mesh(name+'_glazing','glass');rings=[]
            for radius,angles in ((d/2+.08,[-a+2*a*j/6 for j in range(7)]),(d/2+.02,[a-2*a*j/6 for j in range(7)])):
                for t in angles:rings.append([m.vertex((x+radius*math.cos(t)*math.cos(j/64*math.tau),y+radius*math.cos(t)*math.sin(j/64*math.tau),z+radius*math.sin(t))) for j in range(64)])
            for lo,hi in zip(rings,rings[1:]+rings[:1]):
                for j in range(64):k=(j+1)%64;m.face(lo[j],lo[k],hi[k],hi[j])
            out.append(m.finish())
    for i,q in enumerate(S['members']):out.append(rod(q.get('id',f'member_{i}'),q['from_m'],q['to_m'],q['r_m'],q.get('r1_m'),16 if detailed else 10))
    return out


def validate(S):
    if S['kind']=='highrise':
        p=S['plan_m'];rows=S['sections']
        if abs(area(p))<1e-6 or any(math.dist(a,b)<1e-7 for a,b in zip(p,p[1:]+p[:1])):raise ValueError('plan_m needs nonzero area and distinct consecutive points (do not repeat its first point)')
        if len(rows)<2 or rows[0]['z_m']!=0 or rows[-1]['z_m']!=S['h_m']:raise ValueError('sections must run from z_m 0 to h_m')
        if any(a['z_m']>b['z_m'] for a,b in zip(rows,rows[1:])):raise ValueError('sections z_m must not decrease; equal heights form a setback')
        if S.get('crown_slope_m',0)>S['h_m']-rows[-2]['z_m']:raise ValueError('crown_slope_m must fit above the penultimate section')
        o=S.get('opening')
        if o:
            if not 0<o['z0_m']<o['z1_m']<S['h_m']:raise ValueError('opening must be strictly within the tower height')
            if any(q.get('turn_deg',0)!=rows[0].get('turn_deg',0) for q in rows):raise ValueError('a through-opening requires a constant section bearing')
            for z,w in ((o['z0_m'],o['w0_m']),(o['z1_m'],o['w1_m'])):
                p=plan(S,section_at(S,z))
                if w<=0 or min(max(x for x,y in p),-min(x for x,y in p))<=w/2:raise ValueError('opening must leave a pier on both sides')
    else:
        ids=[q['id'] for q in S['spheres']+S['members'] if q.get('id')]
        if len(ids)!=len(set(ids)):raise ValueError('sphere/member ids must be unique')
        if any(math.dist(q['from_m'],q['to_m'])<1e-6 for q in S['members']):raise ValueError('member endpoints must differ')
    meshes=build(S)
    top=max(p[2] for m in meshes for p in m['v'])
    if abs(top-S['h_m'])>.5:raise ValueError(f'geometry top {top:g} does not close to h_m {S["h_m"]:g}')


def build(S,detailed=False): return {'highrise':highrise,'broadcast_tower':broadcast_tower}[S['kind']](S,detailed)


def selftest():
    import collections,unittest
    class Tests(unittest.TestCase):
        def closed(self,m):
            edges=collections.Counter(tuple(sorted((a,b))) for f in m['f'] for a,b in zip(f,f[1:]+f[:1]))
            self.assertTrue(edges);self.assertEqual(set(edges.values()),{2})
            vol=sum(sum(m['v'][f[0]][i]*cross(m['v'][f[1]],m['v'][f[2]])[i] for i in range(3)) for f in m['f'])/6
            self.assertGreater(vol,0)
        def test_sphere_and_inclined_member_closed(self):
            self.closed(sphere('sphere',(0,0,93),50));self.closed(rod('brace',(0,0,0),(60,0,93),3.5))
        def test_twist_notch_and_height(self):
            s={'kind':'highrise','h_m':300,'plan_m':[[-20,-20],[20,-20],[20,20],[4,20],[0,12],[-4,20],[-20,20]],'sections':[{'z_m':0},{'z_m':300,'scale':[.55,.55],'turn_deg':120}]}
            validate(s);m=build(s)[0];self.closed(m);self.assertEqual(max(v[2] for v in m['v']),300)
            self.assertGreater(len(m['v']),len(s['plan_m'])*2)
        def test_aperture_is_real_void(self):
            s={'kind':'highrise','h_m':492,'plan_m':[[-29,-29],[29,-29],[29,29],[-29,29]],'sections':[{'z_m':0},{'z_m':492,'scale':[1,.1]}],'opening':{'z0_m':430,'z1_m':480,'w0_m':24,'w1_m':38}}
            validate(s);ms=build(s)
            self.assertEqual(len(ms),4)
            for m in ms:self.closed(m)
            for m in ms:
                if m['name'].startswith('opening_'):self.assertTrue(all(abs(x)>=12-1e-8 for x,y,z in m['v']))
        def test_bad_opening_and_top_refused(self):
            s={'kind':'highrise','h_m':100,'plan_m':[[-10,-10],[10,-10],[10,10],[-10,10]],'sections':[{'z_m':0},{'z_m':100}],'opening':{'z0_m':90,'z1_m':120,'w0_m':8,'w1_m':8}}
            with self.assertRaises(ValueError):validate(s)
        def test_asymmetric_sloping_crown_keeps_documented_top(self):
            s={'kind':'highrise','h_m':632,'plan_m':[[-30,-50],[45,-20],[25,40],[-20,30]],
               'sections':[{'z_m':0},{'z_m':605,'scale':[.56,.56],'turn_deg':-120},{'z_m':632,'scale':[.56,.56],'turn_deg':-120}],
               'crown_slope_m':27,'crown_direction_deg':167}
            validate(s);m=build(s)[0];self.closed(m)
            self.assertEqual(max(p[2] for p in m['v']),632)
            direction=math.radians(s['crown_direction_deg']);project=lambda p:p[0]*math.cos(direction)+p[1]*math.sin(direction)
            values=[project(p) for p in plan(s,s['sections'][-1])];low,high=min(values),max(values)
            for p in m['v']:
                if p[2]>605:self.assertLessEqual(p[2],632-27*(high-project(p))/(high-low)+1e-7)
        def test_detailed_sphere_glazing_is_a_closed_outer_shell(self):
            s={'kind':'broadcast_tower','h_m':200,'spheres':[{'z_m':100,'d_m':50}],
               'members':[{'from_m':[0,0,0],'to_m':[0,0,200],'r_m':2}]}
            m=build(s,detailed=True)[1];self.closed(m)
            self.assertEqual(m['material'],'glass')
        def test_thin_crown_fin_is_closed(self):
            self.closed(panel('fin',[(6,0,370),(7,0,370),(11,0,382),(6,0,378)],.35))
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not r.wasSuccessful():raise SystemExit(1)


if __name__=='__main__':
    if sys.argv[1:]==['selftest']:selftest()
    else:print(__doc__)
