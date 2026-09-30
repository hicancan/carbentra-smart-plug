import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from sexpr_util import parse,ser,ch
p=Path(sys.argv[1]);s=parse(p.read_text())
def props(fp):return {v[1].strip('"'):v[2].strip('"') for v in fp if isinstance(v,list) and v[0]=='property'}
def geometry(s):
 out={}
 for f in s:
  if not(isinstance(f,list) and f[0]=='footprint'):continue
  ref=props(f)['Reference'];out[ref]={'at':ch(f,'at')[1:],'pads':[{'num':v[1],'at':ch(v,'at')[1:],'size':ch(v,'size')[1:],'drill':ch(v,'drill'),'net':ch(v,'net')[2] if ch(v,'net') else None} for v in f if isinstance(v,list) and v[0]=='pad']}
 return out
r={'status':'reviewed development copper recipe, not manufacturing authorization','geometry':geometry(s),'net_names':{v[1]:v[2] for v in s if isinstance(v,list) and v[0]=='net'},'copper':[v for v in s if isinstance(v,list) and v[0] in ('segment','via','zone')],'stackup':ch(ch(s,'setup'),'stackup'),'rules':p.with_suffix('.kicad_dru').read_text(),'project':json.loads(p.with_suffix('.kicad_pro').read_text())}
p.with_name('routing_recipe.json').write_text(json.dumps(r,indent=2));print(p,len(r['copper']))
