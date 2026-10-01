"""Verify current firmware evidence; shared checks require an explicit platform checkout."""
from pathlib import Path
import argparse,hashlib,json,os,sys
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--local-only',action='store_true',help='Verify independent firmware scope only; never claims cross-repository integration');args=p.parse_args()
e=json.loads((R/'firmware/validation.json').read_text(encoding='utf-8'));checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok,detail=''):checks.append({'check':name,'passed':bool(ok),'detail':detail})
for name,digest in e.get('source_sha256',{}).items():check('source '+name,(R/name).is_file() and sha(R/name)==digest)
for name,digest in e.get('test_evidence_sha256',{}).items():check('evidence '+name,(R/name).is_file() and sha(R/name)==digest)
for name,digest in e.get('artifact_sha256',{}).items():check('binary '+name,(R/'firmware/artifacts'/name).is_file() and sha(R/'firmware/artifacts'/name)==digest)
check('actual ESP32-C3 build',e.get('target')=='esp32c3' and e.get('actual_target_build')=='PASS' and 'Project build complete.' in (R/'firmware/target_build.log').read_text(encoding='utf-8'))
config=(R/'firmware/sdkconfig').read_text(encoding='utf-8');check('actuation disabled',e.get('actuation_enabled') is False and '# CONFIG_CARBENTRA_ALLOW_ACTUATION is not set' in config)
check('certificate dates enabled',e.get('tls_certificate_dates_enabled') is True and 'CONFIG_MBEDTLS_HAVE_TIME_DATE=y' in config)
check('C host regressions',e.get('host_policy_cases',0)>=45 and e.get('host_local_trip_invariants')==10000 and e.get('host_startup_mock_scenarios')==7)
source=e.get('source_sha256',{});check('complete firmware source inventory',all(p.relative_to(R).as_posix() in source for d in ['firmware/core','firmware/main'] for p in (R/d).rglob('*') if p.is_file() and p.suffix in ('.c','.h')))
check('source snapshot digest',hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest()==e.get('source_snapshot_sha256'))
check('legacy edge retired',not any((R/'edge').glob('*.py')) and not any((R/'contracts').glob('*.schema.json')))
if not args.local_only:
 platform=Path(os.environ.get('CARBENTRA_PLATFORM_ROOT','/nonexistent'))
 check('explicit shared platform source',platform.is_dir() and (platform/'packages/iot-contract').is_dir())
 shared=e.get('shared_edge',{});check('shared suite no unexpected skips',shared.get('tests',0)>0 and shared.get('unexpected_skips')==[] and shared.get('skipped')==len(shared.get('platform_specific_skips',[])) and all('test_presence_auth.py' in item and 'POSIX' in item for item in shared.get('platform_specific_skips',[])) and shared.get('direct_dependency_lock_matches') is True)
 for name,digest in shared.get('source_sha256',{}).items():check('shared source '+name,(platform/name).is_file() and sha(platform/name)==digest)
 mqtt=e.get('shared_mqtt_integration',{});proof=R/'firmware/evidence/shared-mqtt-integration.json'
 check('current source-bound shared MQTT proof',mqtt.get('status')=='CURRENT_SOURCE_PASS' and proof.is_file() and sha(proof)==mqtt.get('proof_sha256'))
 for name,digest in mqtt.get('source_sha256',{}).items():check('MQTT shared source '+name,(platform/name).is_file() and sha(platform/name)==digest)
 check('cross-repository proof current',e.get('full_release_evidence_current') is True)
out={'scope':'Independent firmware source/build/host consistency only' if args.local_only else 'Current firmware + explicit shared Edge source/build/software proof; no physical qualification','passed':all(c['passed'] for c in checks),'checks':checks}
(R/'release/firmware_evidence_checks.json').write_text(json.dumps(out,indent=2)+'\n', encoding='utf-8', newline='\n');print(json.dumps({'passed':out['passed'],'scope':out['scope'],'checks':len(checks),'failures':[c['check'] for c in checks if not c['passed']]},indent=2));sys.exit(0 if out['passed'] else 1)
