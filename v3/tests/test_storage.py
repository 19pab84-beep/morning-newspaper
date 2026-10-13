"""Storage boundaries work without private edition fixtures."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from v3.build import build, ROOT
from v3.renderer.press import external_assets

class StorageGates(unittest.TestCase):
    def test_repository_manuscript_and_output_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            for input_path, output in [(ROOT/'editions/input.json', Path(tmp)),
                                       (Path(tmp)/'input.json', ROOT/'output')]:
                with self.assertRaisesRegex(ValueError, 'outside the repository'):
                    build(input_path, Path(tmp)/'state.json', output)

    def test_repository_assets_and_missing_configuration_rejected(self):
        for value in ('', str(ROOT/'assets')):
            with patch.dict(os.environ, {'PORANNA_PRASA_ASSETS': value}):
                with self.assertRaises(ValueError):
                    external_assets()

    def test_external_assets_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {'PORANNA_PRASA_ASSETS': tmp}):
                self.assertEqual(external_assets(), Path(tmp).resolve())
