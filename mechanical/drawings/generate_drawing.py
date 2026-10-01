#!/usr/bin/python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
"""Dimensioned layout drawing. All values sourced from development geometry inputs."""
import json,os,math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('DejaVu',FONT_REGULAR))
pdfmetrics.registerFont(TTFont('DejaVu-Bold',FONT_REGULAR))
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=json.load(open(BASE+'/design_parameters.json'))
out=BASE+'/drawings/CARBENTRA-P16-EVT-A_general_arrangement.pdf'
c=canvas.Canvas(out,pagesize=(1190.55,841.89));c.setTitle('CARBENTRA-P16-EVT-A Development General Arrangement')
navy=HexColor('#14353b');grey=HexColor('#566c71');teal=HexColor('#14847a')
c.setStrokeColor(navy);c.setFillColor(navy);c.rect(25,25,1140,790)
c.setFont('DejaVu-Bold',24);c.drawString(48,775,'CARBENTRA / CARBENTRA-P16')
c.setFont('DejaVu',12);c.drawString(48,750,'Unified campus smart socket | Mechanical general arrangement | Development revision A')
c.setFont('DejaVu-Bold',11);c.setFillColor(HexColor('#ad502c'));c.drawRightString(1145,775,'FABRICATION + ENERGIZATION HOLD')
def txt(x,y,t,size=10):c.setFillColor(navy);c.setFont('DejaVu',size);c.drawString(x,y,t)
def line(x1,y1,x2,y2):c.setStrokeColor(navy);c.setLineWidth(.7);c.line(x1,y1,x2,y2)
def dim(x1,y1,x2,y2,label):
 line(x1,y1,x2,y2)
 a=math.atan2(y2-y1,x2-x1)
 for x,y,sgn in [(x1,y1,1),(x2,y2,-1)]:
  for da in [-.35,.35]:line(x,y,x+sgn*6*math.cos(a+da),y+sgn*6*math.sin(a+da))
 txt((x1+x2)/2+4,(y1+y2)/2+7,label)
scale=3
# Front elevation, mathematically identical face outline and apertures.
ox,oy=225,520
c.setFillColor(HexColor('#f7f9f8'));c.setStrokeColor(navy);c.roundRect(ox-132,oy-132,264,264,42,fill=1)
for s in P['interface']['slots']:
 c.saveState();c.translate(ox+3*s['x'],oy+3*s['y']);c.rotate(s['angle']);c.setFillColor(navy);c.rect(-3.9,-12.6,7.8,25.2,fill=1,stroke=1);c.restoreState()
c.circle(ox,oy-96,12,fill=0);c.setFillColor(teal);c.circle(ox,oy+99,3.6,fill=1)
txt(ox-68,oy-69,'CARBENTRA',10)
for x in [ox-132,ox+132]:line(x,oy+135,x,oy+162)
dim(ox-132,oy+153,ox+132,oy+153,'88')
for y in [oy-132,oy+132]:line(ox-137,y,ox-170,y)
dim(ox-162,oy-132,ox-162,oy+132,'88')
txt(118,365,'FRONT / looking toward -Z',11);txt(118,349,'R14 envelope; 3 apertures only',10)
# Side section represented exactly nominal shell stack and PCB envelope
sx,sy=605,520
c.setFillColor(HexColor('#e8edeb'));c.rect(sx,sy-132,165,264,fill=1)
c.setFillColor(HexColor('#ffffff'));c.rect(sx+9,sy-124.8,148.8,249.6,fill=1)
line(sx+138,sy-132,sx+138,sy+132)
c.setFillColor(HexColor('#bc983e'));c.rect(sx-60,sy+41.4,75,19.2,fill=1)
c.setFillColor(teal);c.rect(sx+24,sy-102,4.8,204,fill=1)
c.setDash(4,3);c.rect(sx+28.8,sy-102,55.2,204,fill=0);c.setDash()
c.setFillColor(HexColor('#adb9b5'));c.rect(sx+93,sy-75,48,150,fill=1)
# mark sketch section as layout (not exact section of each opening)
for x in [sx,sx+165]:line(x,sy+137,x,sy+164)
dim(sx,sy+155,sx+165,sy+155,'55')
dim(sx-60,sy-160,sx,sy-160,'20 provisional')
dim(sx,sy-190,sx+24,sy-190,'PCB z8')
txt(820,450,'SIDE / nominal stack-up layout',11)
txt(820,434,'PCB components max z28',10)
txt(820,418,'Carrier starts z31',10)
txt(820,402,'Front wall 2.4; rear floor 3; split z46',10)
# Stack callouts
for yy,t in [(668,'+Z front face'),(641,'z55 exterior'),(624,'z52.6 lid underside'),(607,'z48 shutter envelope'),(590,'z31 carrier underside'),(573,'z28 PCB component ceiling'),(556,'z9.6 PCB top'),(539,'z8 PCB bottom'),(522,'z0 rear plane')]:txt(857,yy,t,10)
# interface inset
c.setFont('DejaVu-Bold',12);c.drawString(50,303,'INTERFACE + ASSEMBLY CONTROL')
notes=[
'1. Nominal dimensions in mm. Drawing is a design input, not a manufacturing release.',
'2. Target: 220 VAC, single 16 A class three-pin connection. No 10 A or universal compatibility.',
'3. Pin/hole gauge geometry, contact force and material selection remain unverified.',
'4. PCB: 72 x 68 x 1.6; four D3.2 holes at global (+/-31, +/-29).',
'5. Carrier is captured on rear-shell ledges by front-lid lugs; no posts pierce the PCB.',
'6. Four rear-access screw axes: (+/-38, +/-24). Thread/torque design is unresolved.',
'7. PE conductor bypasses switching electronics. Geometric continuity is not a resistance test.',
'8. Coupled shutter is an envelope; spring, dual-actuation interlock and probe tests pending.',
'9. Main fuse, thermal cutoff, auxiliary fuse and wiring modeled; ratings/termination unqualified.',
'10. No tolerance, flammability, dielectric, temperature-rise, endurance or certification approval.'
]
for i,t in enumerate(notes):txt(50,282-i*18,t,10)
line(25,80,1165,80);txt(45,59,'CARBENTRA-P16-EVT-A | 2026-09-30 | Original design inspired by form-factor references',11)
txt(45,41,'SOURCE: design_parameters.json + FreeCAD BRep assembly. Not a Xiaomi internal reconstruction.',9)
txt(890,58,'A3 landscape | Scale: diagrammatic',10);txt(1010,41,'Sheet 1 / 1',10)
c.save()
print(out)
