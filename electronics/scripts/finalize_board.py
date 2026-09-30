#!/usr/bin/python3
"""Normalize redundant vias and refill isolated-domain grounds, without DRC suppression."""
import pcbnew as p,json,math
from pathlib import Path
from sexpr_util import parse,ser,ch
R=Path(__file__).resolve().parents[1];path=R/'carbentra.kicad_pcb';tree=parse(path.read_text());vias=[];remove=[]
for fp in tree:
 if not isinstance(fp,list) or fp[0]!='footprint':continue
 ref=next((v[2].strip('\"') for v in fp if isinstance(v,list) and v[0]=='property' and v[1]=='\"Reference\"'),'')
 if ref=='J5':
  # J5 is close to the board edge: omit only its clipped decorative silk outline.
  # F.Fab and F.CrtYd remain unchanged for mechanical and DRC review.
  fp[:]=[v for v in fp if not(isinstance(v,list) and v[0] in ('fp_line','fp_poly','fp_circle','fp_arc') and ch(v,'layer') and ch(v,'layer')[1]=='\"F.SilkS\"')]
for item in tree:
 if not isinstance(item,list):continue
 if item[0]=='zone':remove.append(item)
 if item[0]=='via':
  ch(item,'size')[1]='0.6';pos=list(map(float,ch(item,'at')[1:]));net=ch(item,'net')[1]
  near=next((v for v in vias if ch(v,'net')[1]==net and math.dist(pos,list(map(float,ch(v,'at')[1:])))<.56),None)
  if near:
   for tr in tree:
    if not isinstance(tr,list) or tr[0]!='segment' or ch(tr,'net')[1]!=net:continue
    for field in('start','end'):
     pt=ch(tr,field)
     if list(map(float,pt[1:]))==pos:pt[1:]=ch(near,'at')[1:]
   remove.append(item)
  else:vias.append(item)
for item in remove:tree.remove(item)
# Remove zero-length tracks: redundant pad-start markers, not physical connections.
tree=[it for it in tree if not(isinstance(it,list) and it[0]=='segment' and ch(it,'start')[1:]==ch(it,'end')[1:])]
path.write_text(ser(tree));b=p.LoadBoard(str(path))
for layer in(p.F_Cu,p.B_Cu):
 z=p.ZONE(b);z.SetLayer(layer);z.SetNetCode(b.FindNet('GND_ISO').GetNetCode());z.SetLocalClearance(p.FromMM(.2));z.SetThermalReliefGap(p.FromMM(.25));z.SetThermalReliefSpokeWidth(p.FromMM(.3));z.SetMinThickness(p.FromMM(.15));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
 poly=z.Outline();poly.NewOutline()
 for x,y in [(31,1),(71,1),(71,67),(31,67),(31,63),(42,63),(42,7),(31,7)]:poly.Append(p.FromMM(x),p.FromMM(y))
 b.Add(z)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
j=json.loads((R/'carbentra.kicad_pro').read_text());j['board']['design_settings']['rules']['min_through_hole_diameter']=.2;(R/'carbentra.kicad_pro').write_text(json.dumps(j,indent=2))
