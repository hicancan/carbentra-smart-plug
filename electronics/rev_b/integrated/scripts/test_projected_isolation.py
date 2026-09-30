from pathlib import Path
import subprocess,os,json,pcbnew as p
R=Path(__file__).resolve().parents[1];O=R/'validation/rule_controls';b=p.LoadBoard(str(R/'integrated.kicad_pcb'))
for f in b.GetFootprints():
 if f.GetReference()=='PS201':
  for q in f.Pads():
   if q.GetNumber()=='9':q.SetPosition(q.GetPosition()+p.VECTOR2I(p.FromMM(.5),0))
path=O/'projected_negative.kicad_pcb';out=O/'projected_negative.json';p.SaveBoard(str(path),b);env=dict(os.environ,CM_AUDIT_BOARD=str(path),CM_AUDIT_OUTPUT=str(out));subprocess.run(['/usr/bin/python3',str(R/'scripts/audit_isolation.py')],env=env,capture_output=True,check=True);r=json.loads(out.read_text());assert not r['pass'];print('PASS: independent checker rejected synthetic shifted hot pad; minimum',r['minimum_mm'])
