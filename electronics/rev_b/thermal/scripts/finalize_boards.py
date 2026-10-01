#!/usr/bin/python3
"""Remove only verified unnecessary fine-pitch escape vias after routing."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
def parse(s):
 st=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s):
  if t=='(':
   a=[]
   if st:st[-1].append(a)
   st.append(a)
  elif t==')':root=st.pop()
  else:st[-1].append(t)
 return root
def ser(x):return '('+' '.join(map(ser,x))+')' if isinstance(x,list) else x
def ch(x,k):return next((v for v in x if isinstance(v,list) and v[0]==k),None)
p=R/'thermal_controller.kicad_pcb';tree=parse(p.read_text(encoding='utf-8'));remove={(31.5,22.),(26.5,22.),(25.5,18.5),(32.5,20.25)};count=0
for v in list(tree):
 if isinstance(v,list) and v[0]=='via':
  xy=tuple(map(float,ch(v,'at')[1:3]))
  if xy in remove:tree.remove(v);count+=1
p.write_text(ser(tree), encoding='utf-8', newline='\n');print('Removed',count,'verified redundant escape vias; DRC must be rerun')
