from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from sexpr_util import parse,ser,ch
R=Path(__file__).resolve().parents[1];P=R/'carbonmirror.kicad_pcb';s=parse(P.read_text());meter=parse((R.parent/'meter/meter.kicad_pcb').read_text());stack=ch(ch(meter,'setup'),'stackup');setup=ch(s,'setup');setup[:]=[v for v in setup if not(isinstance(v,list) and v[0]=='stackup')];setup.append(stack);P.write_text(ser(s))
