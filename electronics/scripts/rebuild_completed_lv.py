#!/usr/bin/python3
"""Replay verified copper only when the frozen footprint geometry matches exactly.
Usage: /usr/bin/python3 scripts/rebuild_completed_lv.py INPUT.kicad_pcb OUTPUT.kicad_pcb
The recipe is intentionally a reviewed routing source, not a general autorouter.
"""
from pathlib import Path
import pcbnew as p,json,sys,shutil
from sexpr_util import parse,ser,ch
if len(sys.argv)!=3:raise SystemExit(__doc__)
src=Path(sys.argv[1]).resolve();dst=Path(sys.argv[2]).resolve();r=json.loads((Path(__file__).parent/'completed_lv_recipe.json').read_text(encoding='utf-8'));b=p.LoadBoard(str(src))
def geometry(board):
 return {f.GetReference():{'at':[f.GetPosition().x,f.GetPosition().y],'angle':f.GetOrientationDegrees(),'pads':sorted([[x.GetNumber(),x.GetPosition().x,x.GetPosition().y,x.GetSize().x,x.GetSize().y,x.GetDrillSize().x,x.GetDrillSize().y] for x in f.Pads()])} for f in board.GetFootprints()}
if geometry(b)!=r['geometry']:raise SystemExit('Refusing replay: component or pad geometry changed; rerouting and review required.')
net=b.FindNet('L_NC_UNUSED')
if not net:net=p.NETINFO_ITEM(b,'L_NC_UNUSED');b.Add(net)
for f in b.GetFootprints():
 if f.GetReference()=='K1':
  for pad in f.Pads():
   if pad.GetNumber()=='12':pad.SetNetCode(net.GetNetCode())
p.SaveBoard(str(dst),b);tree=parse(dst.read_text(encoding='utf-8'));nm={it[2].strip('"'):it[1] for it in tree if isinstance(it,list) and it[0]=='net'}
tree=[it for it in tree if not(isinstance(it,list) and it[0] in ('segment','via','zone'))]
for entry in r['copper']:
 if entry['net'] not in nm:raise SystemExit('Refusing replay: missing net '+entry['net'])
 it=parse(entry['sexpr']);ch(it,'net')[1]=nm[entry['net']];tree.append(it)
dst.write_text(ser(tree), encoding='utf-8', newline='\n');dst.with_suffix('.kicad_dru').write_text(r['dru'], encoding='utf-8', newline='\n')
if src.with_suffix('.kicad_pro').exists() and src.with_suffix('.kicad_pro')!=dst.with_suffix('.kicad_pro'):shutil.copy2(src.with_suffix('.kicad_pro'),dst.with_suffix('.kicad_pro'))
b=p.LoadBoard(str(dst));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(dst),b)
print('Replayed fixed-placement copper:',dst)
