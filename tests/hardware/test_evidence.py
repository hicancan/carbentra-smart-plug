import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

P = Path(__file__).resolve().parents[2] / 'scripts/validate_hardware_evidence.py'
spec = importlib.util.spec_from_file_location('evidence', P)
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class HardwareEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / 'source').write_bytes(b'abc')
        self.manifest = {'source': {'sha256': hashlib.sha256(b'abc').hexdigest(), 'bytes': 3}}

    def test_matching_snapshot(self):
        self.assertEqual(evidence.verify_hashes(self.root, self.manifest), [])

    def test_same_size_source_change_is_rejected(self):
        (self.root / 'source').write_bytes(b'xyz')
        self.assertEqual(evidence.verify_hashes(self.root, self.manifest), ['source'])

    def test_missing_source_is_rejected(self):
        self.assertEqual(evidence.verify_hashes(self.root, {'missing': '0' * 64}), ['missing'])

    def test_incorrect_size_is_rejected(self):
        self.manifest['source']['bytes'] = 4
        self.assertEqual(evidence.verify_hashes(self.root, self.manifest), ['source'])

    def test_external_path_is_rejected(self):
        self.assertEqual(evidence.verify_hashes(self.root, {'../outside': '0' * 64}), ['../outside'])

    def test_empty_reports_never_claim_pass(self):
        self.assertFalse(evidence.validate(self.root)['passed'])


if __name__ == '__main__':
    unittest.main()
