"""Compose annotated CAD render sheets. No AI imagery or substitute geometry."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,os
V=Path(os.environ.get('CM_OUTPUT_DIR',str(Path(__file__).resolve().parents[1])));R=V/'renders'
CTX=json.loads((V/'exports/render_context.json').read_text()) if (V/'exports/render_context.json').exists() else {'revision':'CM-S16-EVT-A','enclosure_mm':{'width':88,'height':88,'depth':55}}
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(s,b=False):return ImageFont.truetype(BOLD if b else REG,s)
INK='#173c40';GRAY='#657a7c';JADE='#198c76';LINE='#9bb1af';BG='#f5f7f3'
def header(im,title,subtitle):
 d=ImageDraw.Draw(im);d.text((115,80),'CARBONMIRROR  /',font=f(27),fill=GRAY);d.text((410,76),'碳镜校园',font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',27),fill=GRAY);d.text((115,140),title,font=f(69,True),fill=INK);d.text((118,238),subtitle,font=f(27),fill=GRAY);d.line((115,310,im.width-115,310),fill=LINE,width=2)
def footer(im):
 d=ImageDraw.Draw(im);d.line((115,im.height-145,im.width-115,im.height-145),fill=LINE,width=2);d.text((115,im.height-112),CTX['revision']+'  •  ENGINEERING DEVELOPMENT  •  VERIFICATION PENDING',font=f(24),fill=GRAY);d.text((115,im.height-73),'Single three-pin 16 A-class target. Interface dimensions, electrical safety and certification remain unverified.',font=f(23),fill=GRAY)
if (R/'06_exploded_raw.png').exists():
 im=Image.new('RGB',(3400,3100),BG);header(im,'One platform. Visible architecture.','Common mechanical and electronic model  /  exploded assembly');footer(im)
 raw=Image.open(R/'06_exploded_raw.png').convert('RGBA');raw.thumbnail((2080,2390));pos=((im.width-raw.width)//2,365);im.paste(raw,pos,raw)
 a=json.loads((R/'06_exploded_raw_anchors.json').read_text());sx=raw.width/2400;sy=raw.height/2600
 groups=[('FrontLid','FRONT HOUSING','Moulded lid + physical control',0),('ShutterGuide','SHUTTER MECHANISM','Development guide and slider',0),('Carrier','INSULATING CARRIER','Contact support and separation',0),('Contact_N','RECEPTACLE CONTACTS','Three individual contact envelopes',1),('PCB','POWER + CONTROL','One shared board architecture',1),('RearShell','REAR HOUSING','Board mounts and screw locations',1),('Blade_N','INPUT INTERFACE','Single three-pin engineering target',1),('FuseCeramic','BRANCH PROTECTION','Fuse and thermal-cutoff candidates',0)]
 # PCB names derive from source OBJ; never introduce a fictitious part anchor.
 if 'PCB' not in a:
  q=next((n for n in a if 'board' in n.lower() or 'pcb' in n.lower()),None)
  if q:a['PCB']=a[q]
 d=ImageDraw.Draw(im)
 for side in (0,1):
  gs=[g for g in groups if g[3]==side and g[0] in a];gs.sort(key=lambda g:a[g[0]][1]);ys=[550+i*520 for i in range(len(gs))]
  for j,(g,y) in enumerate(zip(gs,ys)):
   name,title,sub,_=g;px=pos[0]+a[name][0]*sx;py=pos[1]+a[name][1]*sy
   x=130 if side==0 else 2730;edge=x+525 if side==0 else x-40;elbow=740 if side==0 else 2660
   d.line([(edge,y+42),(elbow,y+42),(px,py)],fill=LINE,width=3);d.ellipse((px-7,py-7,px+7,py+7),fill=JADE)
   d.text((x,y),title,font=f(29,True),fill=INK);d.text((x,y+59),sub,font=f(21),fill=GRAY)
 im.save(R/'06_exploded_annotated.png')
views=['front','rear','left','right','top','bottom']
if all((R/f'view_{n}.png').exists() for n in views):
 im=Image.new('RGB',(3400,2800),BG);header(im,'Six views. One shared model.','Orthographic inspection  /  source dimensions: '+str(CTX['enclosure_mm']['width'])+' × '+str(CTX['enclosure_mm']['height'])+' × '+str(CTX['enclosure_mm']['depth'])+' mm enclosure');footer(im);d=ImageDraw.Draw(im)
 for i,n in enumerate(views):
  x=115+(i%3)*1080;y=355+(i//3)*1100;pic=Image.open(R/f'view_{n}.png').convert('RGBA');pic.thumbnail((1010,980));im.paste(pic,(x,y),pic);d.text((x+40,y+975),f'{i+1:02d}  {n.upper()}',font=f(29,True),fill=INK)
 im.save(R/'07_six_view_sheet.png')
print('Composed render sheets')

if (R/'08_section_raw.png').exists():
 im=Image.new('RGB',(3000,2800),BG);header(im,'Inside the same enclosure.','Display-only longitudinal half-section  /  common CAD and PCB geometry');footer(im)
 pic=Image.open(R/'08_section_raw.png').convert('RGBA');pic.thumbnail((2700,2250));im.paste(pic,((3000-pic.width)//2,330),pic)
 ImageDraw.Draw(im).text((150,2500),'X = 0 cut plane  •  Native engineering parts are unchanged  •  Package bodies are simplified envelopes',font=f(24),fill=GRAY)
 im.save(R/'08_section_annotated.png')
if (R/'09_pcb_assembly.png').exists():
 im=Image.new('RGB',(3000,2800),BG);header(im,'Source copper. Shared geometry.','Development PCB routing inspection  /  simplified package envelopes  /  mask and tenting unqualified');footer(im)
 pic=Image.open(R/'09_pcb_assembly.png').convert('RGB');pic.thumbnail((2650,2200));im.paste(pic,((3000-pic.width)//2,350))
 im.save(R/'09_pcb_annotated.png')
