import unittest,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from service import Edge,strict_json,recommend_shedding
class Tests(unittest.TestCase):
 def setUp(self):self.e=Edge(':memory:',['CM-TEST'])
 def tearDown(self):self.e.db.close()
 def test_time_nonce(self):
  t,m=self.e.accept('carbonmirror/v1/CM-TEST/hello',json.dumps({'clock_nonce':'a'*32}),1700000001)
  self.assertEqual(m['unix_s'],1700000001);self.assertTrue(t.endswith('/time'))
 def test_unknown_device(self):
  with self.assertRaises(ValueError):self.e.accept('carbonmirror/v1/EVIL/hello','{}')
 def test_duplicate_json(self):
  with self.assertRaises(ValueError):strict_json('{"a":1,"a":2}')
 def test_nan(self):
  with self.assertRaises(ValueError):strict_json('{"a":NaN}')
 def test_exponent_overflow(self):
  with self.assertRaises(ValueError):strict_json('{"known_forward_wh_since_boot":1e999}')
 def test_huge_integer(self):
  with self.assertRaises(ValueError):strict_json('{"a":'+('9'*4000)+'}')
 def test_deep_structure(self):
  with self.assertRaises(ValueError):strict_json('['*2000+'0'+']'*2000)
 def test_bad_counter_type(self):
  x={'device_id':'CM-TEST','boot_epoch':'f'*32,'sample_seq':'1','energy_uncertain_intervals':'bad'}
  with self.assertRaises(ValueError):self.e.accept('carbonmirror/v1/CM-TEST/telemetry',json.dumps(x))
 def test_durable_duplicate(self):
  m={'device_id':'CM-TEST','boot_epoch':'f'*32,'sample_seq':'1','valid':False}
  for _ in range(2):self.e.accept('carbonmirror/v1/CM-TEST/telemetry',json.dumps(m))
  self.assertEqual(self.e.db.execute('select count(*) from telemetry').fetchone()[0],1)
 def test_new_boot(self):
  for ch in 'ab':self.e.accept('carbonmirror/v1/CM-TEST/telemetry',json.dumps({'device_id':'CM-TEST','boot_epoch':ch*32,'sample_seq':'1'}))
  self.assertEqual(self.e.db.execute('select count(*) from telemetry').fetchone()[0],2)
 def test_missing_epoch(self):
  with self.assertRaises(ValueError):self.e.accept('carbonmirror/v1/CM-TEST/telemetry','{"device_id":"CM-TEST","sample_seq":"1"}')
 def test_identity_mismatch(self):
  with self.assertRaises(ValueError):self.e.accept('carbonmirror/v1/CM-TEST/telemetry','{"device_id":"EVIL"}')
 def test_dry_run_excludes_critical(self):
  a={'device_id':'CM-TEST','commissioned':True,'approved':True,'allow_mains_shed':True,'critical':True,'fresh':True,'minimum_dwell_met':True,'active_w':100}
  self.assertEqual(recommend_shedding([a],100)['devices'],[])
  a['critical']=False;self.assertEqual(recommend_shedding([a],100)['devices'],['CM-TEST'])
 def test_stale_excluded(self):
  self.assertEqual(recommend_shedding([{'device_id':'x','fresh':False}],100)['unmet_goal_w'],100)
if __name__=='__main__':unittest.main()
