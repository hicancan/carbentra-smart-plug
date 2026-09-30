"""Rev B original parametric mechanics; no dependency or mutation of Rev A files."""
import FreeCAD as App,Part,math,json,os
import power_links as links
V=App.Vector
BASE=os.path.dirname(os.path.abspath(__file__))
P=json.load(open(BASE+'/design_parameters.json'))
S=P['interface']['slots'];OLD_S=[{'name':'PE','x':0,'y':17,'angle':0},{'name':'L','x':-14,'y':-7,'angle':30},{'name':'N','x':14,'y':-7,'angle':-30}];DX=14-9.5*math.cos(math.pi/6);DY=2.25;DPE=-5.9
F=P['pcb']['mount_centers']
def box(w,h,d,x=0,y=0,z=0):return Part.makeBox(w,h,d,V(x,y,z))
def rr(w,h,r,z,d):
 s=box(w-2*r,h,d,-w/2+r,-h/2,z).fuse(box(w,h-2*r,d,-w/2,-h/2+r,z))
 for x in [-w/2+r,w/2-r]:
  for y in [-h/2+r,h/2-r]:s=s.fuse(Part.makeCylinder(r,d,V(x,y,z)))
 return s.removeSplitter()
def slot(w,l,z,d,x,y,a):
 s=box(w,l,d,-w/2,-l/2,z);s.rotate(V(),V(0,0,1),a);s.translate(V(x,y,0));return s

def base_shape(k,w=108,h=93,d=65,travel=0,left_pawl=0,right_pawl=0,contact_gap=1.7):
 e=P['enclosure'];t=e['wall'];r=e['corner_radius'];sp=d-9;fz=d-2.4;pb=P['pcb']['bottom_z'];pt=pb+P['pcb']['thickness'];cb=d-24;seat=d-21;ct=d-8
 if k=='RFServiceSlackEnvelope':
  # Non-physical reservation for approx44mm of the selected100mm coax.
  return Part.makeCylinder(7.95,4,V(23,35.8,46.5)).cut(Part.makeCylinder(6.1,4.2,V(23,35.8,46.4)))
 if k=='RFAntenna':return box(47,.1,7,-23.5,44,44)
 if k=='RFCoax':
  p=links.Path((36.25,24.6,18.15),(0,0,1));p.line(6.85).turn((0,1,0),5).line(8.85).turn((-1,0,0),5).turn((0,0,1),5).line(7.5).turn((-1,0,0),5).line(1.25)
  return p.pipe(.565)
 if k=='RFConnectorEnvelope':return Part.makeCylinder(1.5,3,V(36.25,24.6,15.15))
 if k=='HeadConnectorEnvelope':return box(3.2,8.8,9,42.4,-3.44,18.4)
 if k.startswith('HeadPigtail_'):
  i=int(k.rsplit('_',1)[1]);y=-7.75+2.54*i
  p=links.Path((13.8272413,y,41.83),(0,0,-1));p.line(3.83+1.2*i).turn((1,0,0),2).line(22.1727587).turn((0,1,0),2).line(7.25).turn((1,0,0),2).turn((0,0,-1),2).line(6.6-1.2*i)
  return p.pipe(.55,1.965,0)
 if k in ['AuxFuseCradle','AuxFuseRetainer']:
  # Captive two-saddle support for the underside auxiliary 1 A cartridge.
  x=-33.1;zc=7.1;pieces=[]
  for yy in [-31.9,-21.9]:
   if k=='AuxFuseCradle':
    q=box(8,3,7.0,x-4,yy,3).cut(Part.makeCylinder(3.2,3.2,V(x,yy-.1,zc),V(0,1,0))).cut(box(6.4,3.2,4,x-3.2,yy-.1,zc))
    q=q.cut(box(.5,3.2,.7,x-4.1,yy-.1,8.8)).cut(box(.5,3.2,.7,x+3.6,yy-.1,8.8))
   else:
    q=box(8.8,3,.6,x-4.4,yy,10.25)
    for sx in [-1,1]:q=q.fuse(box(.4,3,2.05,x-4.4 if sx<0 else x+4,yy,8.8)).fuse(box(.75,3,.5,x-4.4 if sx<0 else x+3.65,yy,8.9))
   pieces.append(q)
  # Side spine joins both saddles; it does not pass through the cartridge or PCB.
  spine=box(.4,13,.6,x-4.4,-31.9,10.25) if k=='AuxFuseRetainer' else box(.8,13,1.0,x-4,-31.9,3)
  s=pieces[0].fuse(pieces[1]).fuse(spine)
  if k=='AuxFuseCradle':
   for yy in [-28,-23]:s=s.fuse(box(3.4,3,1,-38.4,yy-1.5,3)).cut(Part.makeCylinder(.8,1.2,V(-37,yy,2.9)))
  return s.removeSplitter()
 if k=='RearShell':
  s=rr(w,h,r,0,sp-.3).cut(rr(w-2*t,h-2*t,r-t,3,sp+2))
  for p in S:
   s=s.cut(slot(1.8,8.1,-.2,5,p['x'],p['y'],p['angle'])).cut(slot(4,11.5,1,1,p['x'],p['y'],p['angle']))
  for x,y in F:
   s=s.fuse(Part.makeCylinder(3.1,pb-3,V(x,y,3)))
   s=s.cut(Part.makeCylinder(1.3,pb+1,V(x,y,-.1))).cut(Part.makeCylinder(2.4,1.4,V(x,y,-.1)))
  for yy in [-28,-23]:s=s.fuse(Part.makeCylinder(.65,1.1,V(-37,yy,3))).fuse(Part.makeCylinder(1.1,.4,V(-37,yy,4)))
  # Carrier shelves are above the declared component ceiling.
  for y in [-20,20]:
   s=s.fuse(box(w/2-t+.4-28,3,1,28,y-1.5,cb-1)).fuse(box(w/2-t+.4-28,3,1,-w/2+t-.4,y-1.5,cb-1))
  # Board-edge retention clips hold the rear subassembly independently of cap screws.
  for x in [-25,25]:
   for sy in [-1,1]:
    y=sy*(P['pcb']['height']/2+.7)
    beam=box(5,1,pb+2-3,x-2.5,y-(1 if sy<0 else 0),3)
    hook=box(5,2.3,.8,x-2.5,41.9 if sy>0 else -44.2,pt)
    s=s.fuse(beam).fuse(hook)
  # Front-side main fuse shelf; explicit pin clearances, away from main-board plane.
  shelf=box(w/2-t+.4-32,29,1.5,-w/2+t-.4,-14.5,41.5)
  for yy in [-11.25,11.25]:shelf=shelf.cut(Part.makeCylinder(1.8,2,V(-40,yy,41.3)))
  # The new clip carrier is separately clamped on posts, not fused into a redundant shelf.
  # Keep the original interface free of carrier-plate overlap.
  for xx in [-46,-34]:
   for yy in [-11.25,11.25]:s=s.fuse(Part.makeCylinder(2.3,3,V(xx,yy,38))).cut(Part.makeCylinder(.5,6,V(xx,yy,37.8)))
  for yy in [-11.25,11.25]:s=s.fuse(box(7,3,5,-52,yy-1.5,36))
  for yy in [-30,25]:s=s.fuse(box(20,3,5,-52,yy-1.5,36))
  s=s.fuse(box(3,18.75,5,-35.5,-30,36)).fuse(box(3,13.75,5,-35.5,11.25,36))
  s=s.fuse(box(w/2-t+.4-26,2.2,1,-w/2+t-.4,22.8,cb-1))
  for name in links.ROUTES:s=s.cut(links.link_shape(name,'keepout'))
  for xx in [-46,-34]:
   for yy in [-11.25,11.25]:s=s.cut(Part.makeCylinder(.5,7,V(xx,yy,37.8)))
  return s.removeSplitter()
 if k=='FrontLid':
  s=rr(w,h,r,sp,d-sp).cut(rr(w-2*t,h-2*t,r-t,sp-.1,fz-sp+.1))
  for p in S:s=s.cut(slot(2.4,8.8,d-4,6,p['x'],p['y'],p['angle']))
  for (x,y),rad in [(P['controls']['local'],4.2),(P['controls']['rearm'],2.2),(P['controls']['led'],1.4)]:s=s.cut(Part.makeCylinder(rad,6,V(x,y,d-4)))
  for x,y in F:
   boss=Part.makeCylinder(3.1,fz-(pt+.4),V(x,y,pt+.4)).cut(Part.makeCylinder(1.25,55.2-(pt+.3),V(x,y,pt+.3))).cut(Part.makeCylinder(.9,5.7,V(x,y,55.2)))
   s=s.fuse(boss)
  # Long plungers are guided by front-shell sleeves, not unsupported slender rods.
  for xy,outer,inner in [(P['controls']['local'],3.0,1.7),(P['controls']['rearm'],2.7,1.7),(P['controls']['led'],2.3,1.4)]:
   x,y=xy;guide=Part.makeCylinder(outer,fz-34,V(x,y,34)).cut(Part.makeCylinder(inner,fz-33.8,V(x,y,33.9)))
   if xy==P['controls']['local']:
    guide=guide.fuse(Part.makeCylinder(5.5,2.6,V(x,y,fz-2.6))).cut(Part.makeCylinder(1.7,3,V(x,y,fz-2.7))).cut(Part.makeCylinder(4.2,1,V(x,y,d-2.7)))
   elif xy==P['controls']['rearm']:guide=guide.cut(Part.makeCylinder(2.2,2,V(x,y,d-3.6)))
   s=s.fuse(guide)
  # Two cover-mounted snap guides retain the service loop within the reserved bay.
  for xx in [16,30]:
   clip=box(4,4,5.8,xx-2,33.8,45.5).cut(box(3,4.2,4.4,xx-1.5,33.7,46.3))
   clip=clip.cut(box(2,4.2,1,xx+1 if xx==16 else xx-3,33.7,47.9))
   stem=box(2,3,fz-51.2,xx-1,34.3,51.2)
   s=s.fuse(clip).fuse(stem)
  return s.removeSplitter()
 if k=='SeamRing':return rr(w-.1,h-.1,r-.05,sp-.3,.3).cut(rr(w-4.7,h-4.7,r-2.35,sp-.4,.6))
 if k=='RearFinish':return rr(w+.08,h+.08,r+.04,3.5,2.4).cut(rr(w,h,r,3.4,2.6))
 if k=='Carrier':
  s=rr(60,50,4,cb,ct-cb).fuse(box(14,18,5.5,-7,2.1,38.5))
  for p in S:s=s.cut(slot(9,16,40.5 if p['name']=='PE' else seat,ct-(40.5 if p['name']=='PE' else seat)+1,p['x'],p['y'],p['angle']))
  s=s.cut(box(49,3.4,3.5,-.1,9.4,cb-.1))
  s=s.fuse(box(8,8,seat-cb,-12+DX,-28+DY,cb))
  for x,y in [(14-DX,-7+DY),(-8+DX,-24+DY)]:s=s.cut(Part.makeCylinder(2.5,3.3,V(x,y,cb-.1)))
  # Off-centre L power lug preserves the sensor's unbroken insulating pickup patch.
  s=s.cut(box(9,19,2,-12.5+DX,-27+DY,seat))
  # Contact-adjacent TF1 pocket with an accessible retaining cap.
  s=s.cut(Part.makeCylinder(3.6,28,V(-22+DX,-21+DY,51),V(0,1,0))).cut(box(7.2,28,8,-25.6+DX,-21+DY,51))
  s=s.cut(box(2.0,5.4,8,-20.3+DX,-9.7+DY,seat))
  # Captive insulating thermal-sheet recess; not a product insulation certification.
  s=s.cut(box(26,28,.6,-27+DX,-21+DY,seat-.5))
  # Rear-mounted sensor PCB pocket, component-side facing away from contact.
  s=s.cut(box(12.6,12.6,3.6,-22.9+DX,-13.3+DY,cb-.1))
  for x in [-23.6,-11.6]:
   for y in [-14,-2]:s=s.fuse(box(3,3,1.8,x+DX,y+DY,cb-1))
  for yy in [-14,2]:
   s=s.fuse(Part.makeCylinder(2.0,11,V(-27+DX,yy+DY,cb)))
   s=s.cut(box(4.4,4.4,2.4,-28.7+DX,yy-2.2+DY,52)).cut(Part.makeCylinder(.5,7,V(-27+DX,yy+DY,48)))
  s=s.cut(box(26,28,.6,-27+DX,-21+DY,seat-.5))
  s=s.cut(box(4.6,5,1.5,-21.5+DX,-9.5+DY,seat))
  # Power channels are cut after handedness reflection in the wrapper.
  for x in [-26,26]:
   for y in [-21,21]:s=s.fuse(Part.makeCylinder(2,fz-ct,V(x,y,ct)))
  return s.removeSplitter()
 if k=='ThermalPad':return box(26,28,.5,-27,-21,seat-.5)
 if k=='PEChannel':
  # Dedicated insulating duct crosses the board through its right notch.
  s=box(6,9,cb-3,45,12.5,3).cut(box(2.4,4,cb-2,46.8,15,2.9))
  s=s.cut(box(2.2,3.4,1.4,44.9,15.3,4.3)).cut(box(6.2,3.2,1.2,44.9,18.4,cb-1.1))
  return s
 if k in ['PEBus','PEBusClearance']:
  rad=1.5 if k=='PEBus' else 1.7;th=1 if k=='PEBus' else 1.4;dz=0 if k=='PEBus' else -.2
  def flat(a,b,z):
   dx,dy=b[0]-a[0],b[1]-a[1];q=box(math.hypot(dx,dy),2*rad,th,0,-rad,z+dz);q.rotate(V(),V(0,0,1),math.degrees(math.atan2(dy,dx)));q.translate(V(a[0],a[1],0))
   return q.fuse(Part.makeCylinder(rad,th,V(a[0],a[1],z+dz))).fuse(Part.makeCylinder(rad,th,V(b[0],b[1],z+dz)))
  s=flat((0,11.1),(48,17),4.5)
  s=s.fuse(box(1 if k=='PEBus' else 1.4,2*rad,cb-4.5+th,47 if k=='PEBus' else 46.8,17-rad,4.5+dz))
  for a,b in [((48,17),(30,17)),((30,17),(20,11.1)),((20,11.1),(0,11.1))]:s=s.fuse(flat(a,b,cb))
  return s.removeSplitter()
 if k.startswith('Blade_') or k.startswith('BladeSleeve_'):
  n=k.rsplit('_',1)[1];p=next(p for p in S if p['name']==n)
  if k.startswith('BladeSleeve_'):return slot(1.8,8.1,-9,9,p['x'],p['y'],p['angle']).cut(slot(1.2,7.5,-9.1,9.2,p['x'],p['y'],p['angle']))
  if n=='PE':s=slot(1.8,8.1,-21,26,p['x'],p['y'],p['angle'])
  else:s=slot(1.8,8.1,-18,9,p['x'],p['y'],p['angle']).fuse(slot(1.2,7.5,-9,9,p['x'],p['y'],p['angle'])).fuse(slot(1.8,8.1,0,5 if n=='L' else 3.2,p['x'],p['y'],p['angle']))
  if n=='N':s=s.fuse(Part.makeCylinder(1.2,3.5,V(p['x'],p['y'],3)))
  return s.fuse(slot(4,11.5,1,1,p['x'],p['y'],p['angle'])).removeSplitter()
 if k.startswith('Contact_'):
  p=next(p for p in OLD_S if p['name']==k[8:]);bottom=40.5 if k=='Contact_PE' else seat
  s=box(5,10,1.3,-2.5,-5,bottom)
  # Original dual formed-leaf spring candidate: 0.4 mm nominal leaf, 1.7 mm free gap.
  # Parameter contact_gap represents the separate elastic inserted-state opening.
  for sign in [-1,1]:
   pts=[(2.1,bottom+1.2),(2.5,bottom+1.2),(2.5,bottom+2.2),(contact_gap/2+.4,52),(contact_gap/2+.4,53.3),(1.6,55.3),(1.2,55.3),(contact_gap/2,53.3),(contact_gap/2,52),(2.1,bottom+2.2)]
   vv=[V(sign*x,-5,z) for x,z in pts];vv.append(vv[0]);leaf=Part.Face(Part.makePolygon(vv)).extrude(V(0,10,0));s=s.fuse(leaf)
  s=s.removeSplitter();s.rotate(V(),V(0,0,1),p['angle']);s.translate(V(p['x'],p['y'],0))
  if k=='Contact_L':
   for a,b in [((-12,-10),(-8,-17)),((-8,-17),(-8,-24)),((-16,-7),(-19.3,-7))]:
    dx,dy=b[0]-a[0],b[1]-a[1];piece=box(math.hypot(dx,dy),4,1.3,0,-2,seat);piece.rotate(V(),V(0,0,1),math.degrees(math.atan2(dy,dx)));piece.translate(V(a[0],a[1],0))
    s=s.fuse(piece).fuse(Part.makeCylinder(2,1.3,V(a[0],a[1],seat))).fuse(Part.makeCylinder(2,1.3,V(b[0],b[1],seat)))
   s=s.fuse(Part.makeCylinder(3,1.3,V(-8,-24,seat)))
   cup=Part.makeCylinder(3,12,V(-22,-13,51),V(0,1,0)).cut(Part.makeCylinder(2.5,12.2,V(-22,-13.1,51),V(0,1,0))).common(box(4,12.2,8,-22,-13.1,47))
   s=s.fuse(box(1.4,5,7,-20,-9.5,seat)).fuse(cup).cut(Part.makeCylinder(2.5,22,V(-22,-18,51),V(0,1,0)))
  return s.removeSplitter()
 if k.startswith('PowerCore_'):return links.link_shape(k[len('PowerCore_'):],'core')
 if k.startswith('PowerCarrier_'):return links.link_shape(k[len('PowerCarrier_'):],'carrier')
 if k=='MainFuseHolder':
  # Captured45x16mm insulating carrier. CQP clips use direct copper collectors.
  s=box(16,45,2,-48,-22.5,41)
  for yy in [-17.45,-9.85,9.85,17.45]:s=s.cut(Part.makeCylinder(.95,3,V(-40,yy,40.5)))
  for sg in [-1,1]:s=s.cut(box(4.4,9.0,.8,-42.2,sg*13.65-4.5,40.9))
  for xx in [-46,-34]:
   for yy in [-11.25,11.25]:s=s.cut(Part.makeCylinder(.9,3,V(xx,yy,40.5)))
  for name in links.ROUTES:s=s.cut(links.link_shape(name,'keepout'))
  return s.removeSplitter()
 if k=='MainFuseCeramic':return Part.makeCylinder(3.175,19.1,V(-40,-9.55,49.85),V(0,1,0))
 if k in ['MainFuseCap1','MainFuseCap2']:return Part.makeCylinder(3.175,6.35,V(-40,-15.9 if k.endswith('1') else 9.55,49.85),V(0,1,0))
 if k in ['MainFuseClip1','MainFuseClip2']:
  yy=(-1 if k.endswith('1') else 1)*13.65
  s=Part.makeCylinder(3.675,7.1,V(-40,yy-3.55,49.85),V(0,1,0)).cut(Part.makeCylinder(3.15,7.3,V(-40,yy-3.65,49.85),V(0,1,0)))
  s=s.common(box(7.85,7.2,10.3,-43.925,yy-3.6,43)).cut(box(2,7.3,5,-41,yy-3.65,49.85))
  s=s.fuse(box(7.85,7.1,.5,-43.925,yy-3.55,43))
  for xx in [-43.5,-37.0]:s=s.fuse(box(.5,7.1,5.8,xx,yy-3.55,43))
  for yp in [yy-3.8,yy+3.8]:s=s.fuse(box(1.5,.5,4.1,-40.75,yp-.25,39.4)).fuse(box(1.5,1,.5,-40.75,yp-.5,43))
  return s.removeSplitter()
 if k in ['MainFuseCollector1','MainFuseCollector2']:
  sg=-1 if k.endswith('1') else 1
  return box(4,8.6,1.2,-42,sg*13.65-4.3,40.4).fuse(box(4,2,2.6,-42,sg*11.25-1,39)).removeSplitter()
 if k=='MainFuseRetainer':
  s=None
  for yy in [-11.25,11.25]:
   a=box(16,2,1.5,-48,yy-1,54.5)
   for xx in [-46,-34]:a=a.fuse(box(2,2,11.5,xx-1,yy-1,43))
   s=a if s is None else s.fuse(a)
  s=s.fuse(box(1,24.5,1.5,-48,-12.25,54.5))
  for xx in [-46,-34]:
   for yy in [-11.25,11.25]:s=s.cut(Part.makeCylinder(.9,15,V(xx,yy,42.5)))
  return s.removeSplitter()
 if k.startswith('FuseRetainerScrew_'):
  i=int(k.rsplit('_',1)[1]);xx=[-46,-34][i//2];yy=[-11.25,11.25][i%2]
  return Part.makeCylinder(.6,18,V(xx,yy,38)).fuse(Part.makeCylinder(1.4,1,V(xx,yy,56)))
 if k=='ThermalBody':return Part.makeCylinder(2,14.7,V(-22,-14.35,51),V(0,1,0))
 if k in ['ThermalLead1','ThermalLead2']:return Part.makeCylinder(.5,4.8,V(-22,-19 if k.endswith('1') else .2,51),V(0,1,0))
 if k=='ThermalSleeve':return Part.makeCylinder(2.5,21,V(-22,-17.5,51),V(0,1,0)).cut(Part.makeCylinder(2,21.2,V(-22,-17.6,51),V(0,1,0)))
 if k=='ThermalRetainer':
  s=Part.makeCylinder(3.4,18,V(-22,-16,51),V(0,1,0)).cut(Part.makeCylinder(2.6,18.2,V(-22,-16.1,51),V(0,1,0))).common(box(4,18.2,8,-26,-16.1,47))
  for yy in [-14,2]:s=s.fuse(box(4,4,2,-28.5,yy-2,52)).cut(Part.makeCylinder(.9,3,V(-27,yy,51.5)))
  s=s
  return s.removeSplitter()
 if k.startswith('ThermalRetainerScrew_'):
  yy=[-14,2][int(k.rsplit('_',1)[1])]
  return Part.makeCylinder(.6,5.5,V(-27,yy,48.5)).fuse(Part.makeCylinder(1.4,1,V(-27,yy,54)))
 if k=='ShutterGuide':
  s=box(47-2*DX,34,3.8,-23.5+DX,-18+DY,ct).cut(box(43-2*DX,30,4.1,-21.5+DX,-16+DY,ct-.1))
  # Ground aperture is never obstructed by the guide's upper bridge.
  s=s.cut(slot(3.0,9.5,ct-.1,4.2,0,11.1,0))
  # Two overhanging lock fingers and recessed hook tracks require both pawls to retract.
  for sg in [-1,1]:
   xx=21.4-DX if sg>0 else -23.7+DX
   s=s.cut(box(2.3,16,1.1,xx,-9+DY,ct+2.8))
   rib=box(1.2,16,5.2,23.4-DX if sg>0 else -24.6+DX,-9+DY,ct)
   finger=box(3.2,2,1.4,21.4-DX if sg>0 else -24.6+DX,-5+DY,ct+3.8)
   s=s.fuse(rib).fuse(finger)
  springguide=box(6,31,4.2,23.5-DX,-15+DY,ct).cut(box(4,29,3.6,24.7-DX,-14+DY,ct+.8))
  s=s.fuse(springguide).cut(box(4,29,3.6,24.7-DX,-14+DY,ct+.8))
  s=s.cut(box(6.0,16.5,1.8,21.4-DX,-15+DY,ct+.8))
  return s.removeSplitter()
 if k=='ShutterSlider':
  s=box(40-2*DX,16,1.4,-20+DX,-15+DY,ct+1).cut(box(22-2*DX,10,2,-11+DX,-12+DY,ct+.8))
  # Two matched cams, coordinated by the single sliding carrier.
  for x in [-20+DX,11-DX]:
   pts=[V(x,-15+DY,ct+2.4),V(x,-2.5+DY,ct+5.1),V(x,-2.5+DY,ct+2.4),V(x,-15+DY,ct+2.4)]
   s=s.fuse(Part.Face(Part.makePolygon(pts)).extrude(V(9,0,0)))
  for sg in [-1,1]:
   x=(14-DX)*sg
   s=s.cut(box(3.4,6.4,4.0,x-1.7,-10.2+DY,ct+2.0))
   s=s.cut(box(7.7,2.6,2.5,14-DX if sg>0 else -21.7+DX,-8.3+DY,ct+2.8))
   well=Part.makeCylinder(1.5,1.1,V(x,-7+DY,ct+1))
   s=s.fuse(well).cut(Part.makeCylinder(1.0,2.2,V(x,-7+DY,ct+1.2)))
  # Moving spring seat/lug on the right of the slider.
  s=s.fuse(box(7.7,3,1.4,19-DX,-15+DY,ct+1)).fuse(Part.makeCylinder(1.45,.35,V(26.7-DX,-12.35+DY,ct+2.4),V(0,1,0)))
  s=s.cut(box(3.0,22,7,-1.5,-5.9,ct+.8))
  s.translate(V(0,travel,0));return s.removeSplitter()
 if k in ['Pawl_L','Pawl_N']:
  sg=-1 if k.endswith('L') else 1;x=(14-DX)*sg;drop=left_pawl if sg<0 else right_pawl
  s=Part.makeCylinder(.45,1.0,V(x,-7+DY,ct+2.0))
  # Pin-facing head follows the insertion cam and pushes the latch down before translation.
  pts=[V(x-1.4,-10+DY,ct+3.0),V(x-1.4,-10+DY,ct+3.525),V(x-1.4,-4+DY,ct+4.875),V(x-1.4,-4+DY,ct+3.0),V(x-1.4,-10+DY,ct+3.0)]
  s=s.fuse(Part.Face(Part.makePolygon(pts)).extrude(V(2.8,0,0)))
  arm=box(7.6,2,.6,14-DX if sg>0 else -21.6+DX,-8+DY,ct+3.9)
  s=s.fuse(arm)
  # Chamfered return-facing hook provides a re-latching cam; the forward face remains square.
  xx=21.4-DX if sg>0 else -22.8+DX
  pts=[V(xx,-8+DY,ct+3.6),V(xx,-6+DY,ct+4.5),V(xx,-6+DY,ct+3.9),V(xx,-8,ct+3.9),V(xx,-8+DY,ct+3.6)]
  # A four-vertex monotonic wedge avoids self-intersection at the thin leading lip.
  pts=[V(xx,-8+DY,ct+3.7),V(xx,-6+DY,ct+4.5),V(xx,-6+DY,ct+3.9),V(xx,-8+DY,ct+3.6),V(xx,-8+DY,ct+3.7)]
  s=s.fuse(Part.Face(Part.makePolygon(pts)).extrude(V(1.4,0,0)))
  s.translate(V(0,travel,-drop));return s.removeSplitter()
 if k in ['PawlSpring_L','PawlSpring_N']:
  sg=-1 if k.endswith('L') else 1;drop=left_pawl if sg<0 else right_pawl
  height=1.66-drop;radius=.67;wire=.06
  helix=Part.makeHelix(height/5,height,radius)
  profile=Part.Wire([Part.makeCircle(wire,V(radius,0,0),V(0,1,height/(2*math.pi*radius*5)))])
  s=Part.Wire(helix.Edges).makePipeShell([profile],True,True)
  s.translate(V(sg*(14-DX),-7+DY+travel,ct+1.28));return s
 if k=='ShutterSpringGuide':
  s=box(5,31,4.2,23.5,-15,ct).cut(box(3.8,29,3.6,24.1,-14,ct+.8))
  s=s.cut(box(3.6,16,1.8,23.4,-15,ct+.8))
  return s.removeSplitter()
 if k=='ShutterReturnSpring':
  height=26.75-travel;radius=1.175;wire=.125
  helix=Part.makeHelix(height/9,height,radius)
  profile=Part.Wire([Part.makeCircle(wire,V(radius,0,0),V(0,1,height/(2*math.pi*radius*9)))])
  s=Part.Wire(helix.Edges).makePipeShell([profile],True,True)
  s.rotate(V(),V(1,0,0),-90);s.translate(V(26.7-DX,-11.875+DY+travel,ct+2.4));return s
 if k in ['LocalButton','RearmButton','StatusLightGuide']:
  is_local=k=='LocalButton';is_light=k=='StatusLightGuide'
  xy=P['controls']['local' if is_local else 'led' if is_light else 'rearm'];x,y=xy
  rad=3.95 if is_local else 1.2 if is_light else 1.95
  top=d if is_light else d-.2 if is_local else d-1.0
  bottom=P['controls']['led_top_z_provisional' if is_light else 'switch_top_z_provisional']
  return Part.makeCylinder(rad,2.4,V(x,y,top-2.4)).fuse(Part.makeCylinder(1.2 if is_light else 1.5,top-bottom-1,V(x,y,bottom))).removeSplitter()
 if k.startswith('Screw_'):
  x,y=F[int(k.split('_')[1])];s=Part.makeCylinder(1.1,d-7,V(x,y,1.2)).fuse(Part.makeCylinder(2.2,1,V(x,y,.2)))
  return s.cut(box(3,.65,.6,x-1.5,y-.325,.1))
 raise ValueError(k)

def shape(k,w=108,h=93,d=65,travel=0,left_pawl=0,right_pawl=0,contact_gap=1.7):
 s=base_shape(k,w,h,d,travel,left_pawl,right_pawl,contact_gap)
 if k in ['Contact_L','ThermalPad','ThermalBody','ThermalLead1','ThermalLead2','ThermalSleeve','ThermalRetainer'] or k.startswith('ThermalRetainerScrew_'):s.translate(V(DX,DY,0))
 elif k=='Contact_N':s.translate(V(-DX,DY,0))
 elif k=='Contact_PE':s.translate(V(0,DPE,0))
 if k in ['Carrier','Contact_L','Contact_N','ThermalPad','ThermalBody','ThermalLead1','ThermalLead2','ThermalSleeve','ThermalRetainer'] or k.startswith('ThermalRetainerScrew_'):
  mat=App.Matrix();mat.A11=-1;s.transformShape(mat,True,False)
 if k in ['ThermalSleeve','ThermalRetainer']:s=s.cut(links.link_shape('L_FUSE_THERMAL','keepout'))
 if k=='ThermalPad':s=s.cut(shape('Contact_PE',w,h,d)).cut(slot(2.4,8.8,43.3,1,0,11.1,0))
 if k=='Carrier':
  s=s.cut(box(2.8,7.9,2.2,12.5,-9.2,39.7))
  for name in links.ROUTES:s=s.cut(links.link_shape(name,'keepout'))
  s=s.cut(shape('PEBusClearance',w,h,d))
  s=s.cut(shape('ThermalRetainer',w,h,d))
  for yy in [-14+DY,2+DY]:s=s.cut(Part.makeCylinder(.9,3,V(27-DX,yy,51.7)))
  s=s.cut(shape('Contact_L',w,h,d))
 if k=='AuxFuseCradle':s=s.cut(shape('RearShell',w,h,d))
 if k=='PEChannel':s=s.cut(shape('PEBusClearance',w,h,d))
 if k in ['RearShell','MainFuseHolder']:s=s.cut(links.ROUTES['L_FUSE_THERMAL'].pipe(1.3))
 if k=='Carrier':
  for yy in [-14+DY,2+DY]:s=s.cut(Part.makeCylinder(1.5,2,V(27-DX,yy,54.3)))
 return s

CACHE={}
class SocketBPart:
 def __init__(self,obj,kind):
  obj.addProperty('App::PropertyString','PartKind').PartKind=kind
  obj.addProperty('App::PropertyString','GeometryRole').GeometryRole='clearance_envelope' if kind=='RFServiceSlackEnvelope' else 'physical_part'
  for n,v in [('Width',108),('Height',93),('Depth',65),('ShutterTravel',0),('LeftPawlStroke',0),('RightPawlStroke',0),('ContactGap',1.7)]:obj.addProperty('App::PropertyLength',n,'Design');setattr(obj,n,v)
  obj.Proxy=self
 def execute(self,obj):
  vals=(obj.PartKind,float(obj.Width),float(obj.Height),float(obj.Depth),float(obj.ShutterTravel),float(obj.LeftPawlStroke),float(obj.RightPawlStroke),float(obj.ContactGap))
  if vals not in CACHE:CACHE[vals]=shape(*vals)
  s=CACHE[vals].copy();obj.Shape=s;obj.Placement=s.Placement
 def dumps(self):return None
 def loads(self,state):pass
