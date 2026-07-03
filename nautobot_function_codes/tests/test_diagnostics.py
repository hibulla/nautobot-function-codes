"""Diagnostics tests."""

from nautobot.apps.testing import TestCase

from nautobot_function_codes.diagnostics import collect_plugin_diagnostics


class PluginDiagnosticsTest(TestCase):
    """Test plugin diagnostic helpers."""

    def test_collect_plugin_diagnostics_passes(self):
        results = collect_plugin_diagnostics()
        checks = {result.check: result for result in results}

        self.assertEqual(checks["plugin_models"].status, "ok")
        self.assertEqual(checks["assignment_ui_routes"].status, "ok")
        self.assertEqual(checks["assignment_list_http"].status, "ok")
