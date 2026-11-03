"""Recorte convexo propio para unir calles sin superficies coplanares duplicadas."""
import math
EPS=1e-7
def area(poly):return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1]))/2
def ccw(poly):return poly if area(poly)>0 else list(reversed(poly))
def clip_half(poly,a,b,inside=True):
    if not poly:return []
    output=[]
    def distance(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    for p,q in zip(poly,poly[1:]+poly[:1]):
        dp,dq=distance(p),distance(q);pin=dp>=-EPS if inside else dp<=EPS;qin=dq>=-EPS if inside else dq<=EPS
        if pin:output.append(p)
        if pin!=qin and abs(dp-dq)>EPS:
            t=dp/(dp-dq);output.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    clean=[]
    for p in output:
        if not clean or math.dist(p,clean[-1])>1e-6:clean.append(p)
    if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-6:clean.pop()
    return clean if len(clean)>2 and abs(area(clean))>1e-5 else []
def subtract(poly,cutter):
    inside=poly;outside=[]
    for a,b in zip(cutter,cutter[1:]+cutter[:1]):
        piece=clip_half(inside,a,b,False)
        if piece:outside.append(piece)
        inside=clip_half(inside,a,b,True)
        if not inside:break
    return outside
def bounds(p):return min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p)
def intersects(a,b):return not (a[2]<b[0]-EPS or a[0]>b[2]+EPS or a[3]<b[1]-EPS or a[1]>b[3]+EPS)
def difference(polys,cutters):
    output=[];cutters=[(p,bounds(p)) for p in cutters]
    for poly in polys:
        parts=[poly]
        for cut,box in cutters:
            if not intersects(bounds(poly),box):continue
            parts=[p for old in parts for p in (subtract(old,cut) if intersects(bounds(old),box) else [old])]
            if not parts:break
        output.extend(parts)
    return output
def union(polys):
    result=[];previous=[]
    for p in polys:
        result.extend(difference([ccw(p)],previous));previous.append(ccw(p))
    return result
def rect(x0,y0,x1,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
def disk(x,y,r,n=32):return [(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n)) for i in range(n)]
def strip(a,b,width):
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*width/2,dx/length*width/2
    return ccw([(a[0]+nx,a[1]+ny),(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny)])
def point_segment(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def inside(p,poly):return all((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])>=-EPS for a,b in zip(poly,poly[1:]+poly[:1]))
def overlap(a,b):
    if not intersects(bounds(a),bounds(b)):return False
    for poly in [a,b]:
        for p,q in zip(poly,poly[1:]+poly[:1]):
            nx,ny=-(q[1]-p[1]),q[0]-p[0]
            pa=[x*nx+y*ny for x,y in a];pb=[x*nx+y*ny for x,y in b]
            if max(pa)<min(pb)+EPS or max(pb)<min(pa)+EPS:return False
    return True
def intersection(a,b,c,d):
    dx,dy=b[0]-a[0],b[1]-a[1];ex,ey=d[0]-c[0],d[1]-c[1];den=dx*ey-dy*ex
    if abs(den)<EPS:return None
    t=((c[0]-a[0])*ey-(c[1]-a[1])*ex)/den;u=((c[0]-a[0])*dy-(c[1]-a[1])*dx)/den
    return ((a[0]+t*dx,a[1]+t*dy),t,u) if -EPS<=t<=1+EPS and -EPS<=u<=1+EPS else None
