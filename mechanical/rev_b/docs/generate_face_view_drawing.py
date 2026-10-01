#!/usr/bin/env python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
"""Original, dimensioned Rev B drawing only. Does not generate or modify CAD."""
from pathlib import Path
import math, json, html, hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT.parent/'design_parameters.json').read_text(encoding='utf-8'))
W,H=420,297
pdfmetrics.registerFont(TTFont('DV',FONT_REGULAR))
pdfmetrics.registerFont(TTFont('DVB',FONT_REGULAR))
base='CARBENTRA-P16-EVT-B_face_view_polarity'
c=canvas.Canvas(str(ROOT/(base+'.pdf')),pagesize=(W*mm,H*mm))
c.setTitle('CARBENTRA CARBENTRA-P16-EVT-B | Face-view polarity and interface control')
c.setAuthor('CARBENTRA Engineering Development')
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">', '<title>CARBENTRA CARBENTRA-P16-EVT-B Face-view polarity and interface control</title>', '<desc>Original design. Front female L right, rear male L left. Nominal reference dimensions only; manufacturing and energization hold.</desc>', '<rect width="420" height="297" fill="white"/>']
NAV='#17383F'; TEAL='#167E78'; MUT='#60747A'; RED='#A93D2C'; LINE='#A8B9BB'; PALE='#F2F7F6'; GOLD='#B58945'; BLUE='#3379AF'
def color(v):return tuple(int(v[i:i+2],16)/255 for i in (1,3,5))
def line(x1,y1,x2,y2,col=NAV,w=.22,dash=False):
 c.setStrokeColorRGB(*color(col));c.setLineWidth(w*mm);c.setDash(1.5*mm,1*mm) if dash else c.setDash();c.line(x1*mm,(H-y1)*mm,x2*mm,(H-y2)*mm)
 svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}"'+(' stroke-dasharray="1.5 1"' if dash else '')+'/>')
def text(x,y,t,s=3,col=NAV,b=False,anchor='start'):
 c.setFillColorRGB(*color(col));c.setFont('DVB' if b else 'DV',s*mm)
 fun={'start':c.drawString,'middle':c.drawCentredString,'end':c.drawRightString}[anchor];fun(x*mm,(H-y)*mm,t)
 svg.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,sans-serif" font-size="{s}" fill="{col}" font-weight="{700 if b else 400}" text-anchor="{anchor}">{html.escape(t)}</text>')
def rect(x,y,w,h,r=0,fill=None,col=NAV,sw=.3):
 c.setStrokeColorRGB(*color(col));c.setLineWidth(sw*mm);c.setDash()
 if fill:c.setFillColorRGB(*color(fill))
 c.roundRect(x*mm,(H-y-h)*mm,w*mm,h*mm,r*mm,stroke=1,fill=bool(fill))
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill or "none"}" stroke="{col}" stroke-width="{sw}"/>')
def circ(x,y,r,col=NAV,fill=None,sw=.25):
 c.setStrokeColorRGB(*color(col));c.setLineWidth(sw*mm);c.setDash()
 if fill:c.setFillColorRGB(*color(fill))
 c.circle(x*mm,(H-y)*mm,r*mm,fill=bool(fill),stroke=1)
 svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill or "none"}" stroke="{col}" stroke-width="{sw}"/>')
def polygon(pts,col=NAV,fill=None,sw=.25):
 c.setStrokeColorRGB(*color(col));c.setLineWidth(sw*mm);c.setDash()
 if fill:c.setFillColorRGB(*color(fill))
 p=c.beginPath();p.moveTo(pts[0][0]*mm,(H-pts[0][1])*mm)
 for x,y in pts[1:]:p.lineTo(x*mm,(H-y)*mm)
 p.close();c.drawPath(p,stroke=1,fill=bool(fill))
 svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+'" fill="'+(fill or 'none')+f'" stroke="{col}" stroke-width="{sw}"/>')
def arrow(x,y,dx,dy,col=NAV):
 a=math.atan2(dy,dx);L=1.65
 for d in (-.4,.4):line(x,y,x+L*math.cos(a+d),y+L*math.sin(a+d),col,.18)
def dim(x1,y1,x2,y2,label,tx=None,ty=None):
 line(x1,y1,x2,y2,MUT,.18);arrow(x1,y1,x2-x1,y2-y1,MUT);arrow(x2,y2,x1-x2,y1-y2,MUT)
 text((x1+x2)/2 if tx is None else tx,(y1+y2)/2-1.5 if ty is None else ty,label,2.7,MUT,anchor='middle')
def slot(cx,cy,width,length,angle,scale=1,mirror=False,col=NAV,fill=NAV):
 a=math.radians(angle);pts=[]
 for xx,yy in [(-width/2,-length/2),(width/2,-length/2),(width/2,length/2),(-width/2,length/2)]:
  x=xx*math.cos(a)-yy*math.sin(a);y=xx*math.sin(a)+yy*math.cos(a)
  pts.append((cx+(-x if mirror else x)*scale,cy-y*scale))
 polygon(pts,col,fill,.23)
def para(x,y,rows,s=2.65,lead=4.3,col=NAV):
 for i,row in enumerate(rows):text(x,y+i*lead,row,s,col)
def heading(x,y,t):text(x,y,t,3.4,NAV,True)
# Frame and header.
rect(8,8,404,281,0,None,LINE,.25)
text(14,20,'CARBENTRA',6.1,NAV,True)
text(14,27,'CARBENTRA-P16-EVT-B  /  ORIGINAL MECHANICAL DEVELOPMENT',3.05,MUT)
text(405,19,'MANUFACTURING + ENERGIZATION HOLD',3.45,RED,True,'end')
text(405,26,'Reference dimensions only  |  GB 1002 gauge validation open',2.9,RED,False,'end')
line(8,31,412,31,LINE)
# Main face views.
heading(28,38,'01  FRONT / FEMALE')
heading(170,38,'02  REAR / MALE')
text(28,42,'Looking along -Z: +X is viewer right',2.6,MUT)
text(170,42,'Looking along +Z: +X is viewer left',2.6,MUT)
for ox,mirror in [(81,False),(223,True)]:
 oy=100
 rect(ox-54,oy-46.5,108,93,14,PALE,NAV,.38)
 line(ox-49,oy,ox+49,oy,LINE,.15,True);line(ox,oy-41,ox,oy+41,LINE,.15,True)
 for p in P['interface']['slots']:
  xx=(-p['x'] if mirror else p['x']);col={'L':RED,'N':BLUE,'PE':TEAL}[p['name']]
  slot(ox+xx,oy-p['y'],1.8 if mirror else 2.4,8.1 if mirror else 8.8,p['angle'],mirror=mirror,col=col,fill=col)
  if p['name']=='PE':text(ox,oy-19,'PE',3.4,col,True,'middle')
  else:text(ox+(-18 if xx<0 else 18),oy+8,p['name'],3.7,col,True,'middle')
 if not mirror:
  for n,r in [('local',4.2),('rearm',2.2),('led',1.4)]:
   x,y=P['controls'][n];circ(ox+x,oy-y,r,col=TEAL if n=='led' else NAV,fill=TEAL if n=='led' else None)
  text(ox,oy+25,'CARBENTRA',3.7,NAV,True,'middle')
 else:
  for x,y in P['pcb']['mount_centers']:circ(ox-x,oy-y,2.2,MUT,None,.2)
  text(ox,oy+28,'DIRECT REAR VIEW',2.5,MUT,False,'middle')
 text(ox,152,'L RIGHT  /  N LEFT' if not mirror else 'L LEFT  /  N RIGHT',3.2,RED,True,'middle')
 text(ox,156.4,'Nominal housing outline - no supplier body copied',2.3,MUT,False,'middle')
# Overall dimensions.
for x in (27,135):line(x,52,x,46.5,MUT,.18)
dim(27,48,135,48,'108')
for y in (53.5,146.5):line(26,y,15,y,MUT,.18)
dim(18,53.5,18,146.5,'93',13,102)
line(31,61,40,58,MUT,.18);text(41,59,'R14',2.7,MUT)
# Original face controls legend; compact.
text(28,162,'Apertures: 2.4 x 8.8 nominal; controls shown at design coordinates',2.45,MUT)
line(8,166,287,166,LINE)
line(287,31,287,277,LINE)
# Detail inset.
heading(14,174,'03  INTERFACE DATUM DETAIL')
text(14,178.5,'Front view  |  2.5:1 nominal detail  |  units mm',2.55,MUT)
ox,oy,sc=69,222,2.5
line(24,oy,112,oy,LINE,.15,True);line(ox,183,ox,258,LINE,.15,True)
for p in P['interface']['slots']:
 col={'L':RED,'N':BLUE,'PE':TEAL}[p['name']]
 x=ox+sc*p['x'];y=oy-sc*p['y']
 slot(x,y,2.4,8.8,p['angle'],sc,col=col,fill=None)
 circ(x,y,.65,col,fill=col,sw=.15)
 if p['name']=='PE':text(x+7,y-6,'PE',3,col,True)
 else:text(x+(-7 if p['name']=='N' else 7),y-13,p['name'],3,col,True,'middle')
# Coordinates, angle, local origin.
circ(ox,oy,.8,MUT,None,.15);text(ox+2,oy-2,'O (0,0)',2.45,MUT)
xx=9.5*math.cos(math.pi/6);lo=ox-sc*xx;hi=ox+sc*xx;yy=oy+sc*4.75;pe=oy-sc*11.1
for x in (lo,hi):line(x,yy+12,x,260,MUT,.18)
dim(lo,258,hi,258,'16.4545')
line(hi+5,yy,123,yy,MUT,.18);line(ox+5,pe,123,pe,MUT,.18)
dim(120,pe,120,yy,'15.85',128,211)
line(ox-5,pe,23,pe,MUT,.18);line(24,oy,24,oy,MUT,.18)
dim(26,pe,26,oy,'11.10',18,205)
text(14,267,'N long axis +30 deg; L long axis -30 deg about +Z from +Y',2.35,MUT)
text(14,271,'Do not use this drawing as a plug/socket gauge',2.65,RED,True)
# Dimension table.
heading(141,184,'WORLD DATUM COORDINATES')
text(141,190,'NAME',2.65,MUT,True);text(167,190,'X',2.65,MUT,True);text(203,190,'Y',2.65,MUT,True);text(237,190,'AXIS',2.65,MUT,True)
for i,(n,x,y,a,col) in enumerate([('PE','0','+11.1000','0 deg',TEAL),('L','+8.2272413','-4.7500','-30 deg',RED),('N','-8.2272413','-4.7500','+30 deg',BLUE)]):
 ypos=197+i*7
 text(141,ypos,n,3,col,True);text(162,ypos,x,2.8);text(200,ypos,y,2.8);text(235,ypos,a,2.8)
 line(140,ypos+2,280,ypos+2,LINE,.13)
para(141,222,[
 'F = 9.5; X = +/-F cos(30 deg); Y = -F sin(30 deg)',
 'PE is 11.1 above the common datum O.',
 'The source drawing\'s 2.2 body-reference offset',
 'is not added to this original assembly datum.',
 '',
 'Front apertures are design inputs, not qualified',
 'female gauge geometry or contact-force proof.',
 'Center distances do not define safety clearance.'
],2.55,4.55)
# Right column nominal side sketch and constraints.
heading(296,39,'04  AXIAL PROJECTIONS')
text(296,44,'Diagrammatic side layout, not a BRep section',2.45,MUT)
# d dimension 65 at scale1.25, pins scale1.25.
sx,sy,ss=326,66,1.1
rect(sx,sy,65*ss,43,3,PALE,NAV,.3)
rect(sx-21*ss,sy+8,21*ss,3,0,GOLD,GOLD,.25)
rect(sx-18*ss,sy+29,18*ss,3,0,GOLD,GOLD,.25)
rect(sx-9*ss,sy+29,9*ss,3,0,NAV,NAV,.25)
text(sx+35,sy+24,'BODY',3,MUT,True,'middle')
text(300,sy+6,'PE',2.6,TEAL,True);text(300,sy+28,'L/N',2.6,RED,True)
for x in (sx,sx+65*ss):line(x,sy-1,x,sy-9,MUT,.18)
dim(sx,sy-7,sx+65*ss,sy-7,'65')
for x in (sx-21*ss,sx):line(x,sy+11,x,sy+20,MUT,.18)
dim(sx-21*ss,sy+18,sx,sy+18,'21 PE')
for x in (sx-18*ss,sx):line(x,sy+33,x,sy+41,MUT,.18)
dim(sx-18*ss,sy+38,sx,sy+38,'18 L/N')
for x in (sx-21*ss,sx+65*ss):line(x,sy+45,x,sy+53,MUT,.18)
dim(sx-21*ss,sy+51,sx+65*ss,sy+51,'86 overall nominal')
text(296,124,'z = -21 PE  /  -18 L,N  /  0 rear  /  +65 front',2.45,MUT)
heading(296,136,'MALE BLADE REFERENCE')
para(296,143,[
 'Width: 8.10 (+0.00 / -0.22)',
 'Thickness: 1.80 (+0.15 / -0.05)',
 'PE projection: 21 nominal',
 'L/N projection: 18 nominal',
 'Live sleeve length: 9.0 (+0.5 / -0.0)',
 'Sleeve outer envelope and gauges: OPEN'
],2.75,4.8)
heading(296,180,'PACKAGE + RELEASE NOTES')
para(296,187,[
 'Nominal housing: 108 x 93 x 65, R14.',
 'PCB: 100 x 85 x 1.6, R10; bottom z11.5.',
 '4 x D3.2 mounts at (+/-44, +/-36).',
 'Two edge notches retained for power paths.',
 'Original enclosure and internal architecture.',
 'No final collision, thermal, mass, torque,',
 'contact or certification result is claimed.',
 'Finish ring may add 0.08 to nominal W/H.',
 'All unspecified tolerances remain OPEN.'
],2.6,4.6)
heading(296,236,'REFERENCE + INTERPRETATION')
para(296,243,[
 'Volex 2025 GB16C, catalogue PDF p36:',
 'mating-interface cross-check only.',
 'Supplier approvals do not apply to CARBENTRA.',
 'GB 1002-2024 licensed dimensions and gauges',
 'must be checked before interface release.'
],2.55,4.45)
# Verified primary-source links, interactive in PDF and SVG.
for url,x,y,w,h in [(
 'https://www.volex.com/media/0dodxec5/volex-power-cords-catalogue-august-2025.pdf#page=36',296,239,109,10),(
 'https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=F8C9E208891B7BB5AF1B3E64933693C2',296,253,109,10)]:
 c.linkURL(url,(x*mm,(H-y-h)*mm,(x+w)*mm,(H-y)*mm),relative=0,thickness=0)
 svg.append(f'<a href="{html.escape(url, quote=True)}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="transparent"><title>Open primary source</title></rect></a>')
# Footer.
line(8,277,412,277,LINE)
text(14,283,'CARBENTRA-P16-EVT-B  |  2026-09-30  |  Original face-view polarity control',2.6,NAV,True)
text(14,287,'Source: design_parameters.json + socket_b_features.py; Volex interface cross-check. Source links and release gates in docs/README.md.',2.15,MUT)
text(405,283,'A3 landscape  |  Main faces 1:1 at 100%',2.55,MUT,False,'end')
text(405,287,'Reference only - do not scale for manufacture  |  Sheet 1 / 1',2.3,MUT,False,'end')
c.save();svg.append('</svg>');(ROOT/(base+'.svg')).write_text('\n'.join(svg),encoding='utf-8', newline='\n')
snap={'document_revision':'CARBENTRA-P16-EVT-B','title':'CARBENTRA Face-view polarity control','status':'Drawing QA only; not final model validation','source_files':{p.relative_to(ROOT.parent).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT.parent/'design_parameters.json',ROOT.parent/'socket_b_features.py',ROOT.parent/'power_links.py']},'coordinate_check':P['interface']['slots'],'output_files':[base+'.pdf',base+'.svg']}
(ROOT/'drawing_source_snapshot.json').write_text(json.dumps(snap,indent=2)+'\n', encoding='utf-8', newline='\n')
print('Wrote',base+'.pdf and .svg')
