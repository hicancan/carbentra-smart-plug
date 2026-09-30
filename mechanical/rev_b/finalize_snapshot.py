#!/usr/bin/python3
"""Bind the bounded engineering-review snapshot to its measured evidence."""
import json,hashlib,pathlib,datetime
B=pathlib.Path(__file__).resolve().parent;R=B.parents[1]
def read(n):return json.loads((B/n).read_text())
fit=read('integrated_fit_report.json');contact=read('contact_engagement_report.json');conn=read('polarity_connectivity_report.json');ins=read('insulation_domain_report.json');rt=read('export_roundtrip_report.json');sh=read('shutter_kinematic_report.json');man=read('parts_manifest.json')
assert fit['mechanical_all_valid'] and fit['mechanical_all_single_solids']
assert not [r for r in fit['mechanical_intersections'] if not r['intentional_interface']]
assert not [r for r in fit['component_and_lead_intersections'] if not r['intentional_terminal_entry']]
assert not fit['head_intersections']
assert contact['geometric_engagement_pass'] and conn['joint_geometry_pass'] and conn['PE_geometric_fused_solid_count']==1
for s in sh['states']:
 if s['state'].startswith('single_'):assert s['intersections']
 else:assert not s['intersections']
 if s['state'] in ['travel_12.5','open_rest']:assert all(p['blocked_volume_mm3']<1e-5 for p in s['insertion_paths'])
assert ins['nominal_geometric_screen']['met_nominally'] and not ins['inputs_changed_during_run']
for p,v in ins['input_snapshot'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==v['sha256'],p
assert rt['all_mechanical_geometry_numeric_equivalent'] and rt['step_roundtrip_all_valid'] and rt['step_roundtrip_solids']==234
assert rt['relative_volume_difference']<1e-6,rt['relative_volume_difference']
physical=[p for p in man['parts'] if p.get('geometry_role')!='clearance_envelope'];refs=[p for p in man['parts'] if p.get('geometry_role')=='clearance_envelope'];assert len(physical)==71 and len(refs)==1
text=f'''# CARBENTRA CM-S16-EVT-B · Final digital review snapshot

- Envelope:108 ×93 ×65 mm nominal; original design, single16A-class interface
- Mechanical geometry:71 physical parts and1 explicitly non-physical RF slack reservation
- Combined system:234 physical model objects(71 mechanical +144 PCB placement/body/lead +19 remote head); reservation retained only as reference in native CAD
- BRep fit:all valid single solids; zero unintended mechanical, main-board/lead or remote-head intersections. Conductive joints, clip engagement and nominal thread-major/pilot overlaps are listed separately
- Conductive joint geometry:all modeled external interfaces connect; PE forms one continuous solid
- Receptacle spring candidate:0.4 mm leaves,1.7 mm free gap;1.8/1.95 mm prescribed inserted states pass with0.05/0.125 mm displacement per leaf and no rigid insertion obstruction
- Shutter:11 tested states; independent single-pawl attempts are mechanically blocked, both-released travel and full-open passages are clear
- Main-board segregation:{ins['nominal_geometric_screen']['minimum_mm']:.6f} mm minimum nominal exposed-primary to isolated copper, including the filled plane; passes the project8.4 mm geometry screen
- RF slack:remaining44.134 mm of the100 mm coax allocated in a retained service-loop reservation, assumed minimum bend radius6 mm; default-hidden and excluded from physical STEP/mass/procurement
- Export check:source and delivered cleaned BRep geometry match within1e−10 numeric serialization tolerance; STEP roundtrip has234 valid solids, relative summed-volume difference{rt['relative_volume_difference']:.3g}

## Scope and remaining release gates
This freezes the bounded digital review configuration. It is not a fabrication, energization or certification release. Nominal3D separation is not a qualified clearance/creepage result. The remote thermal pickup intentionally relies on0.5 mm solid insulation, whose material, compression, edges and dielectric behavior require qualification. Contact force/fatigue, plug/receptacle gauges, blade sleeves, fuse/thermal coordination, conductor terminations, screw torque/retention, RF connector/slack strain relief, thermal rise, wall-socket loading and EMC remain explicit gates in docs/.

The PCB bodies and several connector/lead geometries are nominal/max envelopes, not complete vendor internal CAD. The RF reservation allocates routing space; it does not pretend to be a purchased component or an exact cable centerline. Exterior/main-current packaging stayed fixed during the final checks.
'''
(B/'VALIDATION_SUMMARY.md').write_text(text)
files=[p for p in B.rglob('*') if p.is_file() and p.suffix in ['.py','.json','.md','.csv','.FCStd','.step','.stl','.pdf','.svg'] and '__pycache__' not in p.parts and p.name!='freeze_manifest.json']
extra=[R/'electronics/rev_b/integrated/integrated.kicad_pcb',R/'electronics/rev_b/integrated/exports/integrated_assembly.obj',R/'electronics/rev_b/integrated/exports/remote_head_assembled.obj']
rows=[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(files+extra)]
out={'brand':'CARBENTRA','revision':'CM-S16-EVT-B','snapshot_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Bounded digital engineering review configuration; not a manufacturing/energization/certification release','physical_mechanical_parts':71,'nonphysical_reservations':1,'combined_physical_objects':234,'all_defined_digital_checks_pass':True,'files':rows}
(B/'freeze_manifest.json').write_text(json.dumps(out,indent=2));(B/'checksums.sha256').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in rows));print(json.dumps({k:v for k,v in out.items() if k!='files'},indent=2))
