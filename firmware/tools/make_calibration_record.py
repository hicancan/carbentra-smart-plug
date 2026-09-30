"""Pack a supplied, measured per-unit ATM90E26 calibration into firmware v2 format.
Does not invent coefficients, provision credentials or write a connected device.
"""
import argparse,json,math,struct,zlib
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('measured_json');p.add_argument('output');args=p.parse_args()
x=json.loads(Path(args.measured_json).read_text())
if x.get('board_revision')!='CM-S16-EVT-B':raise SystemExit('Wrong board revision')
identity=x.get('calibration_id','')
if not isinstance(identity,str) or not 1<=len(identity.encode('ascii'))<=31 or any(s in identity.upper() for s in ['REPLACE','EXAMPLE','TEST','DEMO']):raise SystemExit('A real traceable calibration ID is required')
if x.get('measured_reference_record') is None:raise SystemExit('Reference instrument/conditions/results record required')
a,b=x.get('registers_21_2b'),x.get('registers_31_3a')
if not isinstance(a,list) or not isinstance(b,list) or len(a)!=11 or len(b)!=10 or any(type(v)is not int or not 0<=v<=65535 for v in a+b) or not any(a) or not any(b):raise SystemExit('Provide complete measured register words; no defaults')
k=x.get('meter_constant_pulses_per_kwh')
if type(k) not in (int,float) or not math.isfinite(k) or not 0<k<=1e6:raise SystemExit('Invalid calibrated meter constant')
payload=struct.pack('<II12s32s11H10Hf',0x434d4341,2,b'CM-S16-EVT-B\0',identity.encode(),*a,*b,k)
record=payload+struct.pack('<I',zlib.crc32(payload)&0xffffffff)
Path(args.output).write_bytes(record)
print(f'Wrote {len(record)} bytes; CRC is integrity only, not proof of calibration or authorization. No device was programmed.')
