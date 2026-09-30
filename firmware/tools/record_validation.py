"""Record actual locally produced build/test evidence; never certify hardware."""
from pathlib import Path
import hashlib, json, datetime, shutil
R=Path(__file__).resolve().parents[2]
F=R/'firmware'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
log=(F/'target_build.log').read_text()
tests=(F/'tests/host_results.txt').read_text()
edge=(R/'edge/test_results.txt').read_text()
config=(F/'sdkconfig').read_text()
assert 'Project build complete.' in log
assert 'PASS 37 policy cases and 10000 local-trip invariants' in tests
assert 'PASS feedback qualification:' in tests
assert 'runtime reset and stuck-link regression' in tests
assert 'Ran 23 tests' in edge and edge.rstrip().endswith('OK')
assert '# CONFIG_CM_ALLOW_ACTUATION is not set' in config
sources=[p for folder in ['core','main','tests','tools'] for p in (F/folder).rglob('*') if p.is_file() and p.suffix in ('.c','.h','.py','.sh','.json') and '__pycache__' not in p.parts]
sources += [F/'sdkconfig',F/'sdkconfig.defaults',F/'CMakeLists.txt',F/'partitions.csv',F/'main/Kconfig.projbuild',F/'main/CMakeLists.txt']
sources += [p for p in (R/'edge').rglob('*.py') if '__pycache__' not in p.parts]
artifacts=F/'artifacts';artifacts.mkdir(exist_ok=True)
for src,dst in [('carbonmirror_endpoint.bin','carbonmirror_endpoint_DEV_ACTUATION_DISABLED.bin'),('bootloader/bootloader.bin','bootloader_DEV.bin'),('partition_table/partition-table.bin','partition-table_DEV.bin')]:shutil.copyfile(F/'build'/src,artifacts/dst)
out={'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Development digital evidence only; no connected hardware, no flashing, no mains validation','idf_version':'5.4.3','idf_commit':'ea1c174c1cbb7348bd8ba0ff1eb306246938dd80','target':'esp32c3','actual_target_build':'PASS','actuation_enabled':False,'host_policy_cases':37,'host_local_trip_invariants':10000,'edge_unit_tests':23,'host_protocol_and_meter_reset_regressions':'PASS','host_feedback_qualification_tests':'PASS','asan_ubsan':True,'leak_sanitizer':False,'source_sha256':{str(p.relative_to(R)):sha(p) for p in sorted(set(sources))},'artifact_sha256':{p.name:sha(p) for p in artifacts.glob('*.bin')},'limits':['No actual MCU/radio/broker interoperability testing','No per-unit measured calibration','No real 220V switching or safety qualification','No OTA implementation or provisioned secure boot/flash encryption','No stress test of MQTT task preemption','RAM telemetry can be lost at power failure']}
(F/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Recorded real target build, host and edge test evidence with source/binary SHA-256.')
