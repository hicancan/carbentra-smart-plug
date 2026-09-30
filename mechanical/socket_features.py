"""CM-S16 parametric development geometry. Load this module before FCStd recompute.
No part is dimensioned or approved for mains fabrication. Dimensions are design inputs.
"""
import FreeCAD as App, Part, math, json, os
V=App.Vector
BASE=os.path.dirname(os.path.abspath(__file__))
P=json.load(open(os.path.join(BASE,'design_parameters.json')))
def box(w,h,d,x=0,y=0,z=0):return Part.makeBox(w,h,d,V(x,y,z))
def rr(w,h,r,z,d):
 s=box(w-2*r,h,d,-w/2+r,-h/2,z).fuse(box(w,h-2*r,d,-w/2,-h/2+r,z))
 for x in [-w/2+r,w/2-r]:
  for y in [-h/2+r,h/2-r]:s=s.fuse(Part.makeCylinder(r,d,V(x,y,z)))
 return s.removeSplitter()
def slot(w,l,z,d,x,y,a):
 s=box(w,l,d,-w/2,-l/2,z);s.rotate(V(0,0,0),V(0,0,1),a);s.translate(V(x,y,0));return s
H=json.load(open(os.path.join(BASE,'harness_routes.json')))
def cable(points,r):
 points=[V(*p) for p in points];s=Part.makeSphere(r,points[0])
 for a,b in zip(points,points[1:]):
  v=b-a;s=s.fuse(Part.makeCylinder(r,v.Length,a,v.normalize())).fuse(Part.makeSphere(r,b))
 return s.removeSplitter()
S=P['interface']['slots']; F=P['assembly_fasteners']['centers']
def geo(k,w=88,h=88,d=55):
 e=P['enclosure'];t=e['wall'];r=e['corner_radius'];split=e['split_z']; fw=e['front_wall']
 if k=='RearShell':
  s=rr(w,h,r,0,split-.3).cut(rr(w-2*t,h-2*t,r-t,e['rear_floor'],split+2))
  for p in S:s=s.cut(slot(2.0,6.8,-1,6,p['x'],p['y'],p['angle']))
  for x,y in F:s=s.cut(Part.makeCylinder(1.5,4,V(x,y,-.5))).cut(Part.makeCylinder(2.3,1.1,V(x,y,-.1)))
  for x,y in P['pcb']['mount_centers']:
   boss=Part.makeCylinder(3.1,5,V(x,y,3)).cut(Part.makeCylinder(1.25,6,V(x,y,3)))
   s=s.fuse(boss)
  # Insulating mini-carrier shelf for selected fuse holder; pins pass dedicated bores.
  shelf=box(w/2-t+.4-28,29,1.5,-w/2+t-.4,-14.5,30.5)
  for yy in [-11.25,11.25]:shelf=shelf.cut(Part.makeCylinder(1.6,2,V(-34,yy,30.3)))
  s=s.fuse(shelf)
  s=s.fuse(box(28,h/2-t+.4-34,1.5,-26,34,22.75))
  # Captive carrier rests on ledges above the PCB component ceiling.
  for y in [-20,20]:
   s=s.fuse(box(w/2-t+.4-25,3,1,25,y-1.5,30)).fuse(box(w/2-t+.4-25,3,1,-w/2+t-.4,y-1.5,30))
  return s.removeSplitter()
 if k=='FrontLid':
  s=rr(w,h,r,split,d-split).cut(rr(w-2*t,h-2*t,r-t,split-.1,d-fw-split+.1))
  for p in S:s=s.cut(slot(P['interface']['slot_width'],P['interface']['slot_length'],51,6,p['x'],p['y'],p['angle']))
  for x,y,rad in [(0,-32,4.2),(0,33,1.4)]:s=s.cut(Part.makeCylinder(rad,6,V(x,y,51)))
  for x,y in F:
   boss=Part.makeCylinder(2.6,12,V(x,y,40.6)).cut(Part.makeCylinder(1.2,10,V(x,y,40.5)))
   s=s.fuse(boss)
  return s.removeSplitter()
 if k=='SeamRing':return rr(w-.1,h-.1,r-.05,45.7,.3).cut(rr(w-4.7,h-4.7,r-2.35,45.6,.6))
 if k=='RearAccent':return rr(w+.08,h+.08,r+.04,3.5,2.4).cut(rr(w,h,r,3.4,2.6))
 if k=='Carrier':
  s=rr(54,50,4,31,16)
  for p in S:s=s.cut(slot(9,16,34,15,p['x'],p['y'],p['angle']))
  # peripheral screw/post lands; underside PE bus clearance channel
  s=s.cut(box(40,3.4,3.5,-.1,15.3,30.9))
  for p in S:
   if p['name']!='PE':s=s.cut(Part.makeCylinder(1.5,4,V(p['x'],p['y'],30.9)))
  for x in [-23,23]:
   for y in [-21,21]:s=s.fuse(Part.makeCylinder(2,5.6,V(x,y,47)))
  return s.removeSplitter()
 if k=='ShutterGuide':
  s=box(47,22,3.8,-23.5,-18,47).cut(box(43,18,4.1,-21.5,-16,46.9))
  return s
 if k=='ShutterSlider':
  # single coupled blocking plate; kinematics and dual insertion interlock are unresolved
  return box(40,16,1.4,-20,-15,48).cut(box(22,10,2,-11,-12,47.8))
 if k=='Button':return Part.makeCylinder(3.95,2.4,V(0,-32,52.4)).fuse(Part.makeCylinder(2.5,6,V(0,-32,46.4))).fuse(cable([(0,-29,13.9),(0,-32,46.5)],1.2)).cut(box(10,10,10,-5,-34,3.9)).removeSplitter()
 if k=='LightGuide':return Part.makeCylinder(1.2,5,V(0,33,50)).fuse(Part.makeCylinder(2,1,V(0,33,50))).fuse(cable([(0,31,14.9),(0,33,50.1)],1.2)).cut(box(10,10,10,-5,26,4.9)).removeSplitter()
 if k.startswith('Blade_'):
  p=next(p for p in S if k=='Blade_'+p['name']);return slot(P['interface']['blade_thickness'],P['interface']['blade_width'],-P['interface']['blade_projection'],P['interface']['blade_projection']+5,p['x'],p['y'],p['angle'])
 if k.startswith('Contact_'):
  p=next(p for p in S if k=='Contact_'+p['name'])
  s=box(5,10,12,-2.5,-5,34).cut(box(2.2,11,11,-1.1,-5.5,35.3))
  s.rotate(V(0,0,0),V(0,0,1),p['angle']);s.translate(V(p['x'],p['y'],0));return s
 if k=='PEBus':
  # continuous unswitched PE route around board edge, not through mains switching PCB
  return box(39,3,1,0,15.5,4.5).fuse(box(1,3,27.5,38,15.5,4.5)).fuse(box(39,3,1,0,15.5,31)).fuse(box(1,3,3.3,0,15.5,31)).removeSplitter()
 if k=='AntennaFPC':return box(47,.1,7,-23.5,41.5,33)
 if k=='AntennaCoax':
  def path(r):
   pts=[(20,40.95,36.5),(28,38,32)]
   for i in range(49):
    a=4*math.pi*i/48;rr=r+2.6*i/48
    pts.append((32+rr*math.cos(a),30+rr*math.sin(a),26.5))
   pts.extend([(34,27,18),(29,24,12.565)])
   return pts
  lo,hi=2,5
  for _ in range(30):
   mid=(lo+hi)/2;pts=path(mid);length=sum((V(*b)-V(*a)).Length for a,b in zip(pts,pts[1:]))
   if length<100:lo=mid
   else:hi=mid
  return cable(path((lo+hi)/2),.565)
 if k=='AuxFuseBody':return Part.makeCylinder(2.75,16.5,V(-20.25,37,27),V(1,0,0))
 if k in ['AuxFuseCap1','AuxFuseCap2']:return Part.makeCylinder(2.75,2.5,V(-22.75 if k.endswith('1') else -3.75,37,27),V(1,0,0))
 if k in ['AuxFuseLead1','AuxFuseLead2']:return Part.makeCylinder(.325,3.3,V(-25.75 if k.endswith('1') else -1.55,37,27),V(1,0,0))
 if k=='FuseHolder':
  s=box(9.6,25,11.5,-38.8,-12.5,32)
  s=s.cut(Part.makeCylinder(2.65,20.2,V(-34,-10.1,40.5),V(0,1,0))).cut(box(5.3,20.2,4,-36.65,-10.1,40.5))
  for yy in [-11.25,11.25]:
   s=s.cut(Part.makeCylinder(.75,14,V(-34,yy,31)))
   s=s.cut(Part.makeCylinder(.75,3,V(-34,yy-1.5,40.5),V(0,1,0)))
  return s.removeSplitter()
 if k=='FuseCeramic':return Part.makeCylinder(2.5,15,V(-34,-7.5,40.5),V(0,1,0))
 if k in ['FuseCap1','FuseCap2']:return Part.makeCylinder(2.5,2.5,V(-34,-10 if k.endswith('1') else 7.5,40.5),V(0,1,0))
 if k in ['FuseLead1','FuseLead2']:
  sg=-1 if k.endswith('1') else 1
  return cable([(-34,sg*11.25,28.5),(-34,sg*11.25,40.5),(-34,sg*9.5,40.5)],.5)
 if k=='ThermalBody':return Part.makeCylinder(2,14.7,V(33,-7.35,40),V(0,1,0))
 if k in ['ThermalLead1','ThermalLead2']:
  return Part.makeCylinder(.5,4.8,V(33,-12 if k.endswith('1') else 7.2,40),V(0,1,0))
 if k.startswith('WireCore_') or k.startswith('WireJacket_'):
  route=next(q for q in H['routes'] if k.split('_',1)[1]==q['id'])
  core=cable(route['points'],route.get('conductor_radius',H['conductor_radius']))
  if k.startswith('WireCore_'):return core
  jacket=cable(route['points'],route.get('insulated_radius',H['insulated_radius'])).cut(core)
  # Branch insulators are trimmed around all intentionally joined copper paths.
  if route['id'] in ['L_IN_POST','N_IN']:
   q=next(q for q in H['routes'] if q['id']==('AUX_L_IN' if route['id']=='L_IN_POST' else 'AUX_N'))
   jacket=jacket.cut(cable(q['points'],q['conductor_radius']))
  # Jacket stops at conductor mating surfaces, not inside bare contact metal.
  source=route['from']
  if source.startswith(('Blade_','Contact_','FuseLead','ThermalLead','AuxFuseLead','WireCore_')):jacket=jacket.cut(geo(source,w,h,d))
  if route['to'].startswith(('FuseLead','ThermalLead','AuxFuseLead')):jacket=jacket.cut(geo(route['to'],w,h,d))
  ep=route['points'][-1]
  if route['to'].startswith('J'):jacket=jacket.cut(box(6,6,5,ep[0]-3,ep[1]-3,ep[2]-5))
  return max(jacket.Solids,key=lambda s:s.Volume)
 if k.startswith('Screw_'):
  i=int(k.split('_')[1]);x,y=F[i]
  s=Part.makeCylinder(1.15,45.5,V(x,y,1)).fuse(Part.makeCylinder(2.2,1,V(x,y,0)))
  return s.cut(box(3,.65,.6,x-1.5,y-.325,-.1))
 raise ValueError(k)
SHAPE_CACHE={}
class SocketPart:
 def __init__(self,obj,kind):
  obj.addProperty('App::PropertyString','PartKind').PartKind=kind
  for n,v in [('Width',88),('Height',88),('Depth',55)]:obj.addProperty('App::PropertyLength',n,'Envelope');setattr(obj,n,v)
  obj.Proxy=self
 def execute(self,obj):
  key=(obj.PartKind,float(obj.Width),float(obj.Height),float(obj.Depth)) if obj.PartKind in ['RearShell','FrontLid','SeamRing','RearAccent'] else (obj.PartKind,)
  if key not in SHAPE_CACHE:SHAPE_CACHE[key]=geo(obj.PartKind,float(obj.Width),float(obj.Height),float(obj.Depth))
  shape=SHAPE_CACHE[key].copy();obj.Shape=shape;obj.Placement=shape.Placement
 def dumps(self):return None
 def loads(self,state):pass
