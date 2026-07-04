"""Assignment UI tests."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from nautobot.apps.testing import TestCase

from nautobot_function_codes import models
from nautobot_function_codes.forms.assignment import DeviceFunctionCodeAssignmentBulkEditForm
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device
from nautobot_function_codes.utils import get_device_function_code


class DeviceAssignmentViewTest(TestCase):
    """HTTP-level tests for assignment management UI."""

    @classmethod
    def setUpTestData(cls):
        cls.function_code = fixtures.create_functioncode_with(name="ACC", slug="acc-view")
        cls.other_function_code = fixtures.create_functioncode_with(name="COR", slug="cor-view")
        cls.devices = [
            create_test_device(name="assignment-device-1"),
            create_test_device(name="assignment-device-2"),
            create_test_device(name="assignment-device-3"),
        ]
        user_model = get_user_model()
        if not user_model.objects.filter(is_superuser=True).exists():
            user_model.objects.create_superuser("assignment-view", "assignment-view@example.com", "password")
        cls.user = user_model.objects.filter(is_superuser=True).first()

    def setUp(self):
        self.client.force_login(self.user)

    def test_assignment_list_returns_200(self):
        url = reverse("plugins:nautobot_function_codes:devicefunctioncodeassignment_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_assignment_create_shows_bulk_assign_form(self):
        url = reverse("plugins:nautobot_function_codes:devicefunctioncodeassignment_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="function_code"')
        self.assertContains(response, 'name="devices"')
        self.assertNotContains(response, 'name="device"')
        self.assertContains(response, 'id="id_devices"')
        self.assertContains(response, "multiple")
        self.assertContains(response, "embedded_action_modal")

    def test_assignment_create_post_assigns_multiple_devices(self):
        url = reverse("plugins:nautobot_function_codes:devicefunctioncodeassignment_add")
        response = self.client.post(
            url,
            {
                "function_code": str(self.function_code.pk),
                "devices": [str(device.pk) for device in self.devices[:2]],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_device_function_code(self.devices[0]), self.function_code)
        self.assertEqual(get_device_function_code(self.devices[1]), self.function_code)
        self.assertIsNone(get_device_function_code(self.devices[2]))

    def test_assign_devices_view_get_returns_200(self):
        url = reverse(
            "plugins:nautobot_function_codes:functioncode_assign_devices",
            kwargs={"pk": self.function_code.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="devices"')
        self.assertNotContains(response, 'name="function_code"')
        self.assertContains(response, 'id="id_devices"')
        self.assertContains(response, "multiple")
        self.assertContains(response, "embedded_action_modal")

    def test_assign_devices_view_post_assigns_multiple_devices(self):
        url = reverse(
            "plugins:nautobot_function_codes:functioncode_assign_devices",
            kwargs={"pk": self.function_code.pk},
        )
        response = self.client.post(
            url,
            {
                "devices": [str(device.pk) for device in self.devices[:2]],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_device_function_code(self.devices[0]), self.function_code)
        self.assertEqual(get_device_function_code(self.devices[1]), self.function_code)
        self.assertIsNone(get_device_function_code(self.devices[2]))

    def test_assignment_bulk_edit_updates_function_code(self):
        assignment = models.DeviceFunctionCodeAssignment.objects.create(
            device=self.devices[0],
            function_code=self.function_code,
        )
        url = reverse("plugins:nautobot_function_codes:devicefunctioncodeassignment_bulk_edit")
        response = self.client.post(
            url,
            {
                "pk": [str(assignment.pk)],
                "function_code": str(self.other_function_code.pk),
                "_apply": "Apply",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("jobresult", response.url)
        assignment.refresh_from_db()
        self.assertEqual(assignment.function_code, self.other_function_code)

    def test_assignment_bulk_edit_form_validates(self):
        assignment = models.DeviceFunctionCodeAssignment.objects.create(
            device=self.devices[0],
            function_code=self.function_code,
        )
        form = DeviceFunctionCodeAssignmentBulkEditForm(
            models.DeviceFunctionCodeAssignment,
            {
                "pk": [str(assignment.pk)],
                "function_code": str(self.other_function_code.pk),
            },
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_function_code_detail_shows_assigned_devices_panel(self):
        models.DeviceFunctionCodeAssignment.objects.create(
            device=self.devices[0],
            function_code=self.function_code,
        )
        url = reverse("plugins:nautobot_function_codes:functioncode", kwargs={"pk": self.function_code.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ASSIGNED DEVICES")
        self.assertContains(response, self.devices[0].name)
