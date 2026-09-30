"""Compose annotated CAD render sheets. No AI imagery or substitute geometry."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,os
V=Path(os.environ.get('CARBENTRA_OUTPUT_DIR',str(Path(__file__).resolve().parents[1])));R=V/'renders'
CTX=json.loads((V/'exports/render_context.json').read_text()) if (V/'exports/render_context.json').exists() else {'revision':'CARBENTRA-P16-EVT-A','enclosure_mm':{'width':88,'height':88,'depth':55}}
FONT_FILE=Path(__file__).resolve().parents[2]/'assets/fonts/NotoSansSC-Regular.ttf'
REG=str(FONT_FILE);BOLD=REG
def f(s,b=False):return ImageFont.truetype(BOLD if b else REG,s)
INK='#173c40';GRAY='#657a7c';JADE='#198c76';LINE='#9bb1af';BG='#f5f7f3'
def header(im,title,subtitle):
 d=ImageDraw.Draw(im);d.text((115,80),'CARBENTRA  /',font=f(27),fill=GRAY);d.text((410,76),'碳迹未来',font=ImageFont.truetype(REG,27),fill=GRAY);d.text((115,140),title,font=f(69,True),fill=INK);d.text((118,238),subtitle,font=f(27),fill=GRAY);d.line((115,310,im.width-115,310),fill=LINE,width=2)
def footer(im):
 d=ImageDraw.Draw(im);d.line((115,im.height-145,im.width-115,im.height-145),fill=LINE,width=2);d.text((115,im.height-112),CTX['revision']+'  •  工程开发版本  •  待实物验证',font=f(24),fill=GRAY);d.text((115,im.height-73),'单一三孔 16 A 级工程目标。接口量规、电气安全与认证仍须验证。',font=f(23),fill=GRAY)
if (R/'06_exploded_raw.png').exists():
 im=Image.new('RGB',(3400,3100),BG);header(im,'统一平台，结构可见','共同机械与电子源模型  /  分层爆炸视图');footer(im)
 raw=Image.open(R/'06_exploded_raw.png').convert('RGBA');raw.thumbnail((2080,2390));pos=((im.width-raw.width)//2,365);im.paste(raw,pos,raw)
 a=json.loads((R/'06_exploded_raw_anchors.json').read_text());sx=raw.width/2400;sy=raw.height/2600
 groups=[('FrontLid','前壳与操控','前盖、实体按键与状态灯',0),('ShutterGuide','防护门机构','导向、双拨爪与回位机构',0),('Carrier','绝缘承载结构','插套支撑及绝缘隔离',0),('Contact_N','三极插套','独立导电件及接触结构',1),('PCB','电源、计量与控制','一体化主板架构',1),('RearShell','后壳与安装结构','电路板定位与螺钉安装',1),('Blade_N','三极输入接口','厂家尺寸参考，量规待验证',1),('MainFuseCeramic','分支保护结构','熔断器与温度保护候选件',0)]
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
 im=Image.new('RGB',(3400,2800),BG);header(im,'六面正投影视图','同源几何检查  /  外壳尺寸：'+str(CTX['enclosure_mm']['width'])+' × '+str(CTX['enclosure_mm']['height'])+' × '+str(CTX['enclosure_mm']['depth'])+' mm');footer(im);d=ImageDraw.Draw(im)
 for i,n in enumerate(views):
  x=115+(i%3)*1080;y=355+(i//3)*1100;pic=Image.open(R/f'view_{n}.png').convert('RGBA');pic.thumbnail((1010,980));im.paste(pic,(x,y),pic);d.text((x+40,y+975),f'{i+1:02d}  '+dict(front='正面',rear='背面',left='左侧',right='右侧',top='顶面',bottom='底面')[n],font=f(29,True),fill=INK)
 im.save(R/'07_six_view_sheet.png')
print('Composed render sheets')

if (R/'08_section_raw.png').exists():
 im=Image.new('RGB',(3000,2800),BG);header(im,'纵向剖切，检查内部','显示用纵向半剖  /  同源机械与电路板几何');footer(im)
 pic=Image.open(R/'08_section_raw.png').convert('RGBA');pic.thumbnail((2700,2250));im.paste(pic,((3000-pic.width)//2,330),pic)
 ImageDraw.Draw(im).text((150,2500),'X = 0 剖切面  •  原始工程零件保持完整  •  元件外形为简化封装体',font=f(24),fill=GRAY)
 im.save(R/'08_section_annotated.png')
if (R/'09_pcb_assembly.png').exists():
 im=Image.new('RGB',(3000,2800),BG);header(im,'一体化主板检查','开发阶段主板结构检查  /  简化封装体  /  制板工艺与电气安全待验证');footer(im)
 pic=Image.open(R/'09_pcb_assembly.png').convert('RGB');pic.thumbnail((2650,2200));im.paste(pic,((3000-pic.width)//2,350))
 im.save(R/'09_pcb_annotated.png')
