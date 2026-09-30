"""Verify that development build evidence still matches delivered sources/files."""
from pathlib import Path
import json, hashlib, sys
R=Path(__file__).resolve().parents[1]
p=R/'firmware/validation.json'
if not p.exists():raise SystemExit('Missing firmware validation record')
e=json.loads(p.read_text());checks=[]
def check(name,ok,detail=''):checks.append({'check':name,'passed':bool(ok),'detail':detail})
for name,digest in e['source_sha256'].items():
 f=R/name;check('source '+name,f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==digest)
for name,digest in e['artifact_sha256'].items():
 f=R/'firmware/artifacts'/name;check('binary '+name,f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==digest)
check('recorded target build',e.get('actual_target_build')=='PASS' and e.get('target')=='esp32c3')
check('actuation disabled',e.get('actuation_enabled') is False and '# CONFIG_CM_ALLOW_ACTUATION is not set' in (R/'firmware/sdkconfig').read_text())
check('actual build log','Project build complete.' in (R/'firmware/target_build.log').read_text())
check('host regression evidence',e.get('host_policy_cases')==37 and e.get('host_local_trip_invariants')==10000)
check('edge evidence',e.get('edge_unit_tests')==24)
out={'scope':'Hash and development evidence consistency only; not hardware verification','passed':all(c['passed'] for c in checks),'checks':checks}
(R/'release').mkdir(exist_ok=True);(R/'release/firmware_evidence_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':out['passed'],'checks':len(checks),'failures':[c['check'] for c in checks if not c['passed']]},indent=2));sys.exit(0 if out['passed'] else 1)
