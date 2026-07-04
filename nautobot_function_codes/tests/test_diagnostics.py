"""Diagnostics tests."""

from unittest import mock

from django.contrib.auth import get_user_model
from nautobot.apps.testing import TestCase

from nautobot_function_codes.diagnostics import _assignment_list_http_result, collect_plugin_diagnostics


class PluginDiagnosticsTest(TestCase):
    """Test plugin diagnostic helpers."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        if not user_model.objects.filter(is_superuser=True).exists():
            user_model.objects.create_superuser("diagnostics", "diagnostics@example.com", "password")

    def test_collect_plugin_diagnostics_passes(self):
        results = collect_plugin_diagnostics()
        checks = {result.check: result for result in results}

        self.assertEqual(checks["plugin_models"].status, "ok")
        self.assertEqual(checks["assignment_ui_routes"].status, "ok")
        self.assertEqual(checks["extended_ui_routes"].status, "ok")
        self.assertEqual(checks["plugin_jobs"].status, "ok")
        self.assertEqual(
            checks["assignment_list_http"].status,
            "ok",
            checks["assignment_list_http"].message,
        )

    @mock.patch("django.contrib.auth.get_user_model")
    def test_assignment_list_http_warning_without_superuser(self, mock_get_user_model):
        mock_get_user_model.return_value.objects.filter.return_value.first.return_value = None

        result = _assignment_list_http_result()
        self.assertEqual(result.status, "warning")
        self.assertIn("no superuser", result.message)
