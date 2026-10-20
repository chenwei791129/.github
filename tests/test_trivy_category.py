"""Regression checks for the reusable Trivy workflow (requires PyYAML)."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class TrivyCategoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # BaseLoader preserves the Actions key `on` rather than YAML 1.1 booleans.
        cls.workflow = yaml.load(
            (ROOT / '.github/workflows/trivy-scan.yml').read_text(),
            Loader=yaml.BaseLoader,
        )
        cls.inputs = cls.workflow['on']['workflow_call']['inputs']
        cls.steps = cls.workflow['jobs']['trivy']['steps']

    def test_category_is_optional_and_defaults_to_empty(self):
        self.assertEqual(self.inputs['category']['type'], 'string')
        self.assertEqual(self.inputs['category']['required'], 'false')
        self.assertEqual(self.inputs['category']['default'], '')

    def test_upload_uses_override_or_scan_type_fallback(self):
        upload = next(s for s in self.steps if '/upload-sarif@' in s.get('uses', ''))
        self.assertEqual(
            upload['with']['category'],
            "${{ inputs.category || format('trivy-{0}', inputs.scan-type) }}",
        )
        self.assertEqual(upload['with']['sarif_file'], 'trivy-results.sarif')
        self.assertEqual(upload['if'], '${{ always() && inputs.upload-sarif }}')

    def test_existing_callers_need_no_new_required_input(self):
        self.assertTrue(all(i['required'] == 'false' for i in self.inputs.values()))
        self.assertEqual(self.inputs['scan-type']['default'], 'fs')
        self.assertEqual(self.inputs['upload-sarif']['default'], 'false')

    def test_gating_scan_is_unchanged(self):
        gating = next(s for s in self.steps if s.get('id') == 'gating')
        self.assertNotIn('category', gating['with'])
        self.assertEqual(gating['with']['exit-code'], '${{ inputs.exit-code }}')
        self.assertEqual(gating['with']['format'], 'table')


if __name__ == '__main__':
    unittest.main()
