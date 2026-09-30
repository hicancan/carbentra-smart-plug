from pathlib import Path
import re,json
import pcbnew as p
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
f=R/'thermal_controller.kicad_pcb';t=parse(f.read_text());drop={(21.3,18),(31.5,22),(25.5,18.5),(32.5,18.5)}
t[:]=[v for v in t if not(isinstance(v,list) and v[0]=='via' and tuple(map(float,ch(v,'at')[1:3])) in drop)];f.write_text(ser(t));b=p.LoadBoard(str(f))
for layer in [p.F_Cu,p.B_Cu]:
 tr=p.PCB_TRACK(b);tr.SetStart(p.VECTOR2I(p.FromMM(32.5),p.FromMM(18.5)));tr.SetEnd(p.VECTOR2I(p.FromMM(32.5),p.FromMM(19)));tr.SetWidth(p.FromMM(.15));tr.SetLayer(layer);tr.SetNet(b.FindNet('+3V3_ISO'));b.Add(tr)
p.SaveBoard(str(f),b)
