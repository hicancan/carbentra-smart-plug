"""Original supported solid-Cu power link routes. Dimensions are design inputs.
Circular arcs have explicit centreline forming radii; no capsule-corner substitution.
Custom link forming, ferrule/terminal acceptance and temperatures remain qualification gates.
"""
import FreeCAD as App,Part,math,json,os
V=App.Vector
BASE=os.path.dirname(os.path.abspath(__file__))
P=json.load(open(BASE+'/design_parameters.json'))
PX=9.5*math.cos(math.pi/6);PY=-4.75;DX=14-PX;DY=PY+7
ZENTRY=P['pcb']['bottom_z']+P['pcb']['thickness']+7.5
class Path:
 def __init__(self,start,tangent):self.p=V(*start);self.t=V(*tangent);self.t.normalize();self.start=self.p;self.first_t=self.t;self.edges=[];self.radii=[]
 def line(self,L):
  if L<-1e-7:raise ValueError('Negative line length')
  if L>1e-7:
   q=self.p+self.t*L;self.edges.append(Part.makeLine(self.p,q));self.p=q
  return self
 def turn(self,new_t,R):
  q=V(*new_t) if isinstance(new_t,(list,tuple)) else new_t;q.normalize();co=max(-1,min(1,self.t.dot(q)));a=math.acos(co)
  if a<1e-7:return self
  no=(q-self.t*co);no.normalize();c=self.p+no*R
  mid=c+self.t*(R*math.sin(a/2))-no*(R*math.cos(a/2))
  end=c+self.t*(R*math.sin(a))-no*(R*math.cos(a))
  self.edges.append(Part.Arc(self.p,mid,end).toShape());self.p=end;self.t=q;self.radii.append(R);return self
 def s_offset(self,normal,D,A):
  n=V(*normal) if isinstance(normal,(list,tuple)) else normal;n.normalize();R=(A*A+D*D)/(4*D);a=2*math.atan2(D,A);t0=self.t
  self.turn(t0*math.cos(a)+n*math.sin(a),R);self.turn(t0,R);return self
 def pipe(self,r,trim_start=0,trim_end=0):
  lengths=[e.Length for e in self.edges];total=sum(lengths);lo=trim_start;hi=total-trim_end;chosen=[];cursor=0
  for e,L in zip(self.edges,lengths):
   a=max(lo,cursor);b=min(hi,cursor+L)
   if b>a+1e-8:
    p0=e.FirstParameter+(e.LastParameter-e.FirstParameter)*(a-cursor)/L
    p1=e.FirstParameter+(e.LastParameter-e.FirstParameter)*(b-cursor)/L
    chosen.append(e.Curve.toShape(p0,p1))
   cursor+=L
  first=chosen[0];p=first.Vertexes[0].Point;t=first.tangentAt(first.FirstParameter)
  profile=Part.Wire([Part.makeCircle(r,p,t)])
  return Part.Wire(chosen).makePipeShell([profile],True,False,0)
 def record(self):return {'start_mm':list(self.start),'end_mm':list(self.p),'length_mm':sum(e.Length for e in self.edges),'forming_radii_mm':self.radii,'minimum_radius_mm':min(self.radii) if self.radii else None}
def rear_start(start,xy):
 t=V(xy[0]-start[0],xy[1]-start[1],0);dist=t.Length;t.normalize();p=Path(start,t);p.line(dist-6).turn((0,0,1),6);return p

def routes():
 out={}
 p=Path((PX,PY+1,5.7),(0,-1,0));p.turn((-1,0,0),6).s_offset((0,1,0),2.25,20).line(PX+11).turn((0,-1,0),6).turn((0,0,1),6);A1=math.sqrt(24*8.25-8.25**2);A2=math.sqrt(24*3-3**2);p.line(39-A1-A2-p.p.z).s_offset((0,1,0),8.25,A1).s_offset((1,0,0),3,A2);out['L_RAW']=p
 p=Path((-PX,PY,5.7),(0,1,0));p.line(.75).turn((-1,0,0),6).line(37-PX).turn((0,-1,0),6).line(.5).turn((0,0,1),6);p.line(ZENTRY-6-p.p.z).turn((1,0,0),6).s_offset((0,-1,0),1.38,11);p.line(-21.4-p.p.x);out['N_RAW']=p
 p=Path((-40,11.25,39),(0,1,0));p.line(4.75).turn((0,0,1),6).turn((1,0,0),6).line(50-DX).turn((0,-1,0),6).line(8.75);out['L_FUSE_THERMAL']=p
 p=Path((22-DX,-19+DY,51),(0,-1,0));p.line(2+DY).turn((-1,0,0),6).line(48-DX).turn((0,0,-1),6).s_offset((0,1,0),7.5,math.sqrt(4*6*7.5-7.5*7.5));p.line(p.p.z-(ZENTRY+6)).turn((1,0,0),6).line(10.6);out['L_PROTECTED']=p
 for name,y in [('L_OUTPUT',-3.26),('N_OUTPUT',4.36)]:
  p=Path((-21.4,y,ZENTRY),(-1,0,0));p.line(16.6).turn((0,0,1),6).line(32.8-p.p.z).turn((1,0,0),6)
  if name=='L_OUTPUT':p.s_offset((0,-1,0),20.74-DY,40-DX)
  else:p.line(24-2*PX).s_offset((0,-1,0),11.36-DY,22-DX)
  p.turn((0,0,1),6);out[name]=p
 return out

ROUTES=routes()
CONNECTIONS={
 'L_RAW':('Blade_L','MainFuseCollector1'),
 'N_RAW':('Blade_N','J201.2_N'),
 'L_FUSE_THERMAL':('MainFuseCollector2','ThermalLead2'),
 'L_PROTECTED':('ThermalLead1','J201.1_PROTECTED_L'),
 'L_OUTPUT':('J102.1_SWITCHED_L','Contact_L_lug'),
 'N_OUTPUT':('J102.2_N','Contact_N')}
TRIMS={'L_RAW':(2,1),'N_RAW':(2,8.2),'L_FUSE_THERMAL':(9,1),'L_PROTECTED':(1,8.2),'L_OUTPUT':(8.2,1.3),'N_OUTPUT':(8.2,1.3)}
def link_shape(name,kind='core'):
 p=ROUTES[name]
 if kind=='core':return p.pipe(1.0)
 a,b=TRIMS[name]
 if kind=='keepout':return p.pipe(2.45,a,b)
 s=p.pipe(2.2,a,b).cut(p.pipe(1.2,a,b))
 if name in ['L_RAW','N_RAW']:
  x=PX if name=='L_RAW' else -PX;ang=-30 if name=='L_RAW' else 30
  cut=Part.makeBox(2.2,8.5,3,V(-1.1,-4.25,3));cut.rotate(V(),V(0,0,1),ang);cut.translate(V(x,PY,0));s=s.cut(cut)
  if name=='N_RAW':s=s.cut(Part.makeCylinder(1.4,3.8,V(-PX,PY,3)))
 return max(s.Solids,key=lambda q:q.Volume)

def manifest():
 return {'revision':'B','conductor':'Custom annealed Cu-ETP round Ø2.0mm,3.14mm²; forming/termination not production-qualified','insulation':'Dedicated rigid insulating carriers:nominal outerØ4.4, innerØ2.4,1mm radial wall; resin/insulation class unqualified','installation_radial_allowance_mm':.25,'terminal_entry_height_mm':ZENTRY,'terminal_entry_height_uncertainty_mm':1.0,'terminal_straight_engagement_mm':8.0,'routes':[{'id':n,'from':CONNECTIONS[n][0],'to':CONNECTIONS[n][1],**p.record(),'bare_end_lengths_mm':list(TRIMS[n])} for n,p in ROUTES.items()]}
if __name__=='__main__':
 json.dump(manifest(),open(BASE+'/power_link_manifest.json','w'),indent=2);print(json.dumps(manifest(),indent=2))
 for n in ROUTES:
  for k in ['core','carrier','keepout']:
   s=link_shape(n,k);assert s.isValid() and len(s.Solids)==1,(n,k)
 print('All6 links and their insulation/installation envelopes are valid single solids')
