from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
from pathlib import Path
import sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'));from sexpr_util import *
R=Path(__file__).resolve().parents[1];P=R/'integrated.kicad_pcb';a=parse(P.read_text(encoding='utf-8'));lib=parse(Path(kicad_resource('footprints/Converter_ACDC.pretty/Converter_ACDC_MeanWell_IRM-10-xx_THT.kicad_mod')).read_text(encoding='utf-8'))
for i,f in enumerate(a):
 if not(isinstance(f,list)and f[0]=='footprint' and any(isinstance(v,list)and v[:3]==['property','"Reference"','"PS101"']for v in f)):continue
 new=copy.deepcopy(lib);new[1]='"Converter_ACDC:Converter_ACDC_MeanWell_IRM-10-xx_THT"';new[:]=[v for v in new if not(isinstance(v,list)and v[0]in('version','generator','generator_version','uuid','at','path'))]
 for tag in ('uuid','at','path'):
  if ch(f,tag):new.append(copy.deepcopy(ch(f,tag)))
 oldpads={v[1]:v for v in f if isinstance(v,list)and v[0]=='pad'}
 for v in new:
  if not isinstance(v,list):continue
  if v[0]=='property':
   if v[1]=='"Reference"':v[2]='"PS101"';ch(v,'layer')[1]='"F.Fab"'
   if v[1]=='"Value"':v[2]='"IRM-10-5"';v.append(['hide','yes'])
  if v[0].startswith('fp_') and ch(v,'layer') and ch(v,'layer')[1]=='"F.SilkS"':ch(v,'layer')[1]='"F.Fab"'
  if v[0]=='pad':
   for tag in ('net','pinfunction','pintype'):
    if ch(oldpads[v[1]],tag):v.append(copy.deepcopy(ch(oldpads[v[1]],tag)))
 a[i]=new
P.write_text(ser(a), encoding='utf-8', newline='\n')
