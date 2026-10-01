"""Regression: reject an intentionally6mm hot/cold gap using supported KiCad syntax."""
from pathlib import Path
import pcbnew as p,json,subprocess,os
R=Path(__file__).resolve().parents[1];O=R/'validation/rule_controls';O.mkdir(exist_ok=True)
b=p.BOARD();b.SetCopperLayerCount(4)
for name in ('HOT_TEST','ISO_TEST'):b.Add(p.NETINFO_ITEM(b,name))
for i,(name,x)in enumerate([('HOT_TEST',10),('ISO_TEST',17)]):
 f=p.FOOTPRINT(b);f.SetReference('TP'+str(i+1));f.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(10)));b.Add(f);q=p.PAD(f);q.SetNumber('1');q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetShape(p.PAD_SHAPE_RECT);q.SetSize(p.VECTOR2I(p.FromMM(1),p.FromMM(1)));q.SetPosition(f.GetPosition());ls=p.LSET();ls.AddLayer(p.F_Cu);q.SetLayerSet(ls);q.SetNetCode(b.FindNet(name).GetNetCode());f.Add(q)
for a,z in [((5,5),(25,5)),((25,5),(25,20)),((25,20),(5,20)),((5,20),(5,5))]:
 t=p.PCB_SHAPE();t.SetShape(p.SHAPE_T_SEGMENT);t.SetLayer(p.Edge_Cuts);t.SetStart(p.VECTOR2I(*[p.FromMM(v)for v in a]));t.SetEnd(p.VECTOR2I(*[p.FromMM(v)for v in z]));t.SetWidth(p.FromMM(.05));b.Add(t)
results={}
for kind,cond in [('unsupported',"A.NetName.startsWith('HOT_') && B.NetName == 'ISO_TEST'"),('supported',"(A.NetName == 'HOT_*' && B.NetName == 'ISO_TEST') || (B.NetName == 'HOT_*' && A.NetName == 'ISO_TEST')")]:
 path=O/(kind+'.kicad_pcb');p.SaveBoard(str(path),b);path.with_suffix('.kicad_pro').write_text((R/'integrated.kicad_pro').read_text(encoding='utf-8'), encoding='utf-8', newline='\n');path.with_suffix('.kicad_dru').write_text('(version 1)\n(rule "DOMAIN NEGATIVE CONTROL" (condition "'+cond+'") (constraint clearance (min 8mm)))\n', encoding='utf-8', newline='\n');report=O/(kind+'.json');subprocess.run(['kicad-cli','pcb','drc',str(path),'--format','json','-o',str(report)],capture_output=True,check=True);t=json.loads(report.read_text(encoding='utf-8'));results[kind]={'gap_mm':6,'expected_rule_reported':any(v.get('type')=='clearance' and 'DOMAIN NEGATIVE CONTROL' in v.get('description','') for v in t['violations'])}
results['pass']=not results['unsupported']['expected_rule_reported']and results['supported']['expected_rule_reported'];(O/'result.json').write_text(json.dumps(results,indent=2), encoding='utf-8', newline='\n');print(json.dumps(results,indent=2));assert results['pass']
