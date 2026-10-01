from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from sexpr_util import parse,ser,ch
R=Path(__file__).resolve().parents[1];P=R/'integrated.kicad_pcb';a=parse(P.read_text(encoding='utf-8'));lib=parse(Path(kicad_resource('footprints/Converter_ACDC.pretty/Converter_ACDC_MeanWell_IRM-10-xx_THT.kicad_mod')).read_text(encoding='utf-8'))
for f in a:
 if not(isinstance(f,list)and f[0]=='footprint'):continue
 props={v[1].strip('"'):v for v in f if isinstance(v,list)and v[0]=='property'};ref=props['Reference'][2].strip('"')
 if ref=='PS101':
  f[:]=[v for v in f if not(isinstance(v,list)and v[0]in('descr','tags','model'))]+[v for v in lib if isinstance(v,list)and v[0]in('descr','tags','model')]
P.write_text(ser(a), encoding='utf-8', newline='\n')
