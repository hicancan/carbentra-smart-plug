import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from accounting import Factor,reject_overlapping_meters,purchased_electricity_emissions
class AccountingTests(unittest.TestCase):
 def test_parent_overlap(self):
  with self.assertRaises(ValueError):reject_overlapping_meters(['building','plug'],{'plug':'room','room':'building'})
 def test_siblings(self):reject_overlapping_meters(['plug1','plug2'],{'plug1':'room','plug2':'room'})
 def test_cycle(self):
  with self.assertRaises(ValueError):reject_overlapping_meters(['x'],{'x':'a','a':'b','b':'a'})
 def test_partial_is_not_savings(self):
  f=Factor(0.5,'SYNTHETIC_TEST_ONLY',2000,'https://example.com/synthetic-test')
  r=purchased_electricity_emissions(100,f,True)
  self.assertEqual(r['known_kg_co2e'],50);self.assertEqual(r['coverage'],'partial');self.assertFalse(r['is_verified_reduction'])
 def test_missing_source(self):
  with self.assertRaises(ValueError):Factor(0.5,'test',2000,'').validate()
if __name__=='__main__':unittest.main()
