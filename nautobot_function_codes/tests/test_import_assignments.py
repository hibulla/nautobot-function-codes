"""Tests for CSV import of device assignments."""

import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from nautobot.apps.testing import TestCase

from nautobot_function_codes.services.import_assignments import MAX_CSV_ROWS, import_assignments_from_csv
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device
from nautobot_function_codes.utils import get_device_function_code, set_device_function_code


class ImportAssignmentsServiceTest(TestCase):
    """Test CSV import service logic."""

    user_permissions = (
        "dcim.view_device",
        "dcim.change_device",
        "nautobot_function_codes.view_functioncode",
    )

    @classmethod
    def setUpTestData(cls):
        cls.function_code = fixtures.create_functioncode_with(name="ACC", slug="acc-import")
        cls.other_function_code = fixtures.create_functioncode_with(name="WAN", slug="wan-import")
        cls.inactive_code = fixtures.create_functioncode_with(name="OLD", slug="old-import", is_active=False)
        cls.device = create_test_device(name="import-device-1")
        cls.other_device = create_test_device(name="import-device-2")

    def _csv(self, content):
        """Return CSV content as an in-memory text stream."""
        return io.StringIO(content)

    def test_import_assigns_and_clears_devices(self):
        set_device_function_code(self.other_device, self.other_function_code)
        csv_data = "device,function_code\n" f"{self.device.name},acc-import\n" f"{self.other_device.name},\n"
        result = import_assignments_from_csv(self._csv(csv_data), self.user)
        self.assertEqual(result.updated, 1)
        self.assertEqual(result.cleared, 1)
        self.assertEqual(result.errors, 0)
        self.assertEqual(get_device_function_code(self.device), self.function_code)
        self.assertIsNone(get_device_function_code(self.other_device))

    def test_import_dry_run_does_not_save(self):
        csv_data = f"device,function_code\n{self.device.name},acc-import\n"
        result = import_assignments_from_csv(self._csv(csv_data), self.user, dry_run=True)
        self.assertEqual(result.updated, 1)
        self.assertTrue(result.dry_run)
        self.assertIsNone(get_device_function_code(self.device))

    def test_import_rejects_unknown_device(self):
        csv_data = "device,function_code\nmissing-device,acc-import\n"
        result = import_assignments_from_csv(self._csv(csv_data), self.user)
        self.assertEqual(result.errors, 1)
        self.assertEqual(result.updated, 0)

    def test_import_rejects_inactive_function_code(self):
        csv_data = f"device,function_code\n{self.device.name},old-import\n"
        result = import_assignments_from_csv(self._csv(csv_data), self.user)
        self.assertEqual(result.errors, 1)
        self.assertIsNone(get_device_function_code(self.device))

    def test_import_rejects_csv_over_row_limit(self):
        csv_data = "device,function_code\n" + "\n".join(
            f"missing-device-{index},acc-import" for index in range(MAX_CSV_ROWS + 1)
        )
        with self.assertRaisesRegex(ValueError, f"limited to {MAX_CSV_ROWS} non-empty data rows"):
            import_assignments_from_csv(self._csv(csv_data), self.user)


class ImportAssignmentsViewTest(TestCase):
    """HTTP tests for the import assignments view."""

    user_permissions = (
        "nautobot_function_codes.change_devicefunctioncodeassignment",
        "dcim.view_device",
        "dcim.change_device",
        "nautobot_function_codes.view_functioncode",
    )

    @classmethod
    def setUpTestData(cls):
        cls.function_code = fixtures.create_functioncode_with(name="COR", slug="cor-import-view")
        cls.device = create_test_device(name="import-view-device")

    def test_import_view_get_returns_200(self):
        url = reverse("plugins:nautobot_function_codes:import_assignments")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Import Device Assignments")

    def test_import_view_post_assigns_device(self):
        url = reverse("plugins:nautobot_function_codes:import_assignments")
        csv_content = f"device,function_code\n{self.device.name},cor-import-view\n".encode()
        response = self.client.post(
            url,
            {
                "csv_file": SimpleUploadedFile("assignments.csv", csv_content, content_type="text/csv"),
                "dry_run": False,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "updated=1")
        self.assertEqual(get_device_function_code(self.device), self.function_code)

    def test_import_view_downloads_template(self):
        url = reverse("plugins:nautobot_function_codes:import_assignments")
        response = self.client.get(url, {"export": "template"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("function-code-assignments-template.csv", response["Content-Disposition"])
        self.assertEqual(response.content.decode().splitlines()[0], "device,function_code")

    def test_import_view_exports_current_assignments(self):
        set_device_function_code(self.device, self.function_code)
        url = reverse("plugins:nautobot_function_codes:import_assignments")
        response = self.client.get(url, {"export": "current"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("device,function_code", content)
        self.assertIn(f"{self.device.name},{self.function_code.slug}", content)
