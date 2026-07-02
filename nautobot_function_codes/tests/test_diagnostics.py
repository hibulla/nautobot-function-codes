"""Diagnostics tests."""

from nautobot.apps.testing import TestCase

from nautobot_function_codes.diagnostics import collect_device_integration_diagnostics
from nautobot_function_codes.tests.utils import create_test_device


class DeviceIntegrationDiagnosticsTest(TestCase):
    """Test Device integration diagnostic helpers."""

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device(name="diagnostics-device")

    def test_collect_device_integration_diagnostics_passes(self):
        results = collect_device_integration_diagnostics()
        checks = {result.check: result for result in results}

        self.assertTrue(checks["integration_state"].status == "ok")
        self.assertTrue(checks["device_form_class"].status == "ok")
        self.assertTrue(checks["url_dcim_device_edit"].status == "ok")
        self.assertIn("detail=True", checks["url_dcim_device_edit"].message)

    def test_collect_device_integration_diagnostics_with_device_pk(self):
        results = collect_device_integration_diagnostics(device_pk=self.device.pk)
        checks = {result.check: result for result in results}

        self.assertIn("device_get_object", checks)
        self.assertEqual(checks["device_get_object"].status, "ok")
