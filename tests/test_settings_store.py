import unittest
import os
import tempfile
from src.domain.settings_store import SettingsStore

class TestSettingsStore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.store = SettingsStore(os.path.join(self.test_dir.name, 'settings.json'))

    def tearDown(self):
        self.test_dir.cleanup()

    def test_default_settings_valid(self):
        self.assertTrue(self.store.validate(self.store.get_all()))

    def test_invalid_values_rejected(self):
        with self.assertRaises(ValueError):
            self.store.set('magnification_scale', -1)

    def test_round_trip_save_load(self):
        self.store.set('magnification_scale', 1.5)
        self.store.save()
        new_store = SettingsStore(self.store.path)
        self.assertEqual(new_store.get('magnification_scale'), 1.5)

if __name__ == '__main__':
    unittest.main()
