import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from sexpr_util import parse,ser,ch
p=Path(sys.argv[1]);s=parse(p.read_text());r=json.loads(p.with_name('routing_recipe.json').read_text())
def geometry(s):
 out={}
 for f in s:
  if not(isinstance(f,list) and f[0]=='footprint'):continue
  ref=next(v[2].strip('"') for v in f if isinstance(v,list) and v[0]=='property' and v[1]=='"Reference"');out[ref]={'at':ch(f,'at')[1:],'pads':[{'num':v[1],'at':ch(v,'at')[1:],'size':ch(v,'size')[1:],'drill':ch(v,'drill'),'net':ch(v,'net')[2] if ch(v,'net') else None} for v in f if isinstance(v,list) and v[0]=='pad']}
 return out
if geometry(s)!=r['geometry']:raise SystemExit('REFUSED: footprint or pad geometry/net assignment changed')
nets={v[2]:v[1] for v in s if isinstance(v,list) and v[0]=='net'}
s=[v for v in s if not(isinstance(v,list) and v[0] in ('segment','via','zone'))]
for v in r['copper']:
 net=ch(v,'net')
 if net:net[1]=nets[r['net_names'][net[1]]]
 s.append(v)
if r['stackup']:
 setup=ch(s,'setup');setup[:]=[v for v in setup if not(isinstance(v,list) and v[0]=='stackup')];setup.append(r['stackup'])
p.write_text(ser(s));p.with_suffix('.kicad_dru').write_text(r['rules']);p.with_suffix('.kicad_pro').write_text(json.dumps(r['project'],indent=2));print('Replayed',len(r['copper']),'copper objects')
