#!/usr/bin/python3
from pathlib import Path
import pcbnew as p
from sexpr_util import parse,ser,ch
R=Path(__file__).resolve().parents[1];P=R/'candidate_lv.kicad_pcb';t=parse(P.read_text());nets={x[1]:x[2].strip('"') for x in t if isinstance(x,list) and x[0]=='net'}
# Shift two local traces by at most .125 mm to open U3 ground escape.
for it in t:
 if not isinstance(it,list):continue
 if it[0]=='segment':
  net=nets[ch(it,'net')[1]];a=list(map(float,ch(it,'start')[1:]));z=list(map(float,ch(it,'end')[1:]))
  if net=='TEMP_ALERT':
   for pt in (ch(it,'start'),ch(it,'end')):
    xy=list(map(float,pt[1:]))
    if xy==[56.5,55.625]:pt[1:]=['56.375','55.5']
    elif xy==[57.25,55.625]:pt[1:]=['57.25','55.5']
    elif xy==[56.5,50.875]:pt[1:]=['56.375','50.875']
  if net=='BUTTON':
   for pt in (ch(it,'start'),ch(it,'end')):
    if float(pt[1])==56.1 and 51.4<=float(pt[2])<=55.8:pt[1]='56.05'
  if net=='EN' and a==[45.75,31.25] and z==[45.75,60.0]:
   ch(it,'start')[1]='45.9';ch(it,'end')[1]='45.9'
 if it[0]=='zone':
  poly=ch(it,'polygon');pts=ch(poly,'pts');pts[:]=['pts']+[['xy',str(x),str(y)] for x,y in [(31,1),(71,1),(71,67),(31,67),(31,63),(42,63),(42,58),(46,58),(46,30),(42,30),(42,7),(31,7)]]
t=[it for it in t if not(isinstance(it,list) and it[0]=='segment' and ch(it,'start')[1:]==ch(it,'end')[1:])];P.write_text(ser(t));b=p.LoadBoard(str(P))
# Reattach the original EN endpoints after the 0.15 mm isolation adjustment.
for a,z in [((45.75,31.25),(45.9,31.25)),((45.75,60),(45.9,60))]:
 q=p.PCB_TRACK(b);q.SetStart(p.VECTOR2I(*[p.FromMM(v) for v in a]));q.SetEnd(p.VECTOR2I(*[p.FromMM(v) for v in z]));q.SetWidth(p.FromMM(.15));q.SetLayer(p.F_Cu);q.SetNetCode(b.FindNet('EN').GetNetCode());b.Add(q)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(P),b)
