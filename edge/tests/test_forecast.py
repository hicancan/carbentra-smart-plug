import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from service import forecast_baseline
class ForecastTests(unittest.TestCase):
 def test_constant(self):
  r=forecast_baseline([{'unix_s':i*10,'active_w':100,'valid':True} for i in range(20)])
  self.assertEqual(r['predicted_w'],100);self.assertEqual(r['historical_residual_mad_w'],0)
 def test_linear(self):
  r=forecast_baseline([{'unix_s':i*10,'active_w':i*20,'valid':True} for i in range(20)],100)
  self.assertEqual(r['predicted_w'],580)
 def test_invalid_history(self):self.assertFalse(forecast_baseline([])['valid'])
 def test_no_fake_confidence(self):
  r=forecast_baseline([{'unix_s':i*10,'active_w':100,'valid':True} for i in range(20)])
  self.assertFalse(r['is_calibrated_prediction_interval'])
if __name__=='__main__':unittest.main()
