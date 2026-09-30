#!/usr/bin/python3
"""Capture completed fixed-placement copper as a net-name keyed routing recipe."""
from pathlib import Path
import json,pcbnew as p
from sexpr_util import parse,ser,ch
R=Path(__file__).resolve().parents[1];path=R/'candidate_lv.kicad_pcb';tree=parse(path.read_text());b=p.LoadBoard(str(path))
def geometry(board):
 return {f.GetReference():{'at':[f.GetPosition().x,f.GetPosition().y],'angle':f.GetOrientationDegrees(),'pads':sorted([[x.GetNumber(),x.GetPosition().x,x.GetPosition().y,x.GetSize().x,x.GetSize().y,x.GetDrillSize().x,x.GetDrillSize().y] for x in f.Pads()])} for f in board.GetFootprints()}
nets={it[1]:it[2].strip('"') for it in tree if isinstance(it,list) and it[0]=='net'};copper=[]
for it in tree:
 if not isinstance(it,list) or it[0] not in ('segment','via','zone'):continue
 if it[0]=='zone':it=[v for v in it if not(isinstance(v,list) and v[0]=='filled_polygon')]
 copper.append({'net':nets[ch(it,'net')[1]],'sexpr':ser(it)})
r={'description':'Verified developmental LV copper, fixed 33 component and 4 hole geometry. Nine mains airwires remain intentionally open. Not safety certification.','geometry':geometry(b),'copper':copper,'dru':(R/'candidate_lv.kicad_dru').read_text()};(R/'scripts/completed_lv_recipe.json').write_text(json.dumps(r,indent=2)+'\n')
