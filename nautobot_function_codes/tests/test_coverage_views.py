"""Tests for the coverage dashboard."""

from django.urls import reverse
from nautobot.apps.testing import TestCase

from nautobot_function_codes import models
from nautobot_function_codes.services.coverage import get_audit_report, get_coverage_stats
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device
from nautobot_function_codes.utils import set_device_function_code


class CoverageServiceTest(TestCase):
    """Test coverage statistics helpers."""

    user_permissions = (
        "dcim.view_device",
        "nautobot_function_codes.view_functioncode",
        "nautobot_function_codes.view_devicefunctioncodeassignment",
    )

    @classmethod
    def setUpTestData(cls):
        cls.function_code = fixtures.create_functioncode_with(name="COR", slug="cor-coverage")
        cls.inactive_code = fixtures.create_functioncode_with(
            name="OLD",
            slug="old-coverage",
            is_active=False,
        )
        cls.assigned_device = create_test_device(name="coverage-assigned")
        cls.unassigned_device = create_test_device(name="coverage-unassigned")
        cls.inactive_device = create_test_device(name="coverage-inactive")
        set_device_function_code(cls.assigned_device, cls.function_code)
        models.DeviceFunctionCodeAssignment.objects.create(
            device=cls.inactive_device,
            function_code=cls.inactive_code,
        )

    def test_get_coverage_stats_counts_devices(self):
        stats = get_coverage_stats(self.user)
        self.assertGreaterEqual(stats.total_devices, 3)
        self.assertGreaterEqual(stats.assigned_devices, 2)
        self.assertGreaterEqual(stats.unassigned_devices, 1)
        self.assertGreaterEqual(stats.inactive_assignments, 1)
        self.assertTrue(stats.status_rows)
        self.assertTrue(stats.location_rows)
        self.assertTrue(stats.role_rows)
        self.assertIn("nautobot_function_codes_has_function_code=false", stats.unassigned_devices_url)
        self.assertIn("function_code_is_active=false", stats.inactive_assignments_url)

    def test_get_audit_report_includes_unassigned_and_inactive(self):
        report = get_audit_report(self.user)
        self.assertGreaterEqual(report.unassigned_count, 1)
        self.assertGreaterEqual(report.inactive_assignment_count, 1)
        self.assertTrue(any("Unassigned device:" in line for line in report.log_lines))
        self.assertTrue(any("Inactive assignment:" in line for line in report.log_lines))


class CoverageDashboardViewTest(TestCase):
    """HTTP tests for the coverage dashboard."""

    user_permissions = ("nautobot_function_codes.view_functioncode",)

    @classmethod
    def setUpTestData(cls):
        cls.function_code = fixtures.create_functioncode_with(name="DIS", slug="dis-dashboard")

    def test_coverage_dashboard_returns_200(self):
        url = reverse("plugins:nautobot_function_codes:coverage_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Function Code Coverage")
        self.assertContains(response, self.function_code.name)
        self.assertContains(response, "Coverage by Status")
        self.assertContains(response, "Inactive Assignments")
