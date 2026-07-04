"""Device integration tests."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from nautobot.apps.testing import TestCase
from nautobot.dcim.models import Device

from nautobot_function_codes import models
from nautobot_function_codes.filter_extensions import DeviceFilterExtension
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device
from nautobot_function_codes.utils import (
    assign_devices_to_function_code,
    get_device_function_code,
    set_device_function_code,
    unassign_devices,
)


class DeviceFunctionCodeIntegrationTest(TestCase):
    """Test Device assignment helpers and filter extension field naming."""

    @classmethod
    def setUpTestData(cls):
        cls.function_code = fixtures.create_functioncode_with(name="DIS", slug="dis")
        cls.other_function_code = fixtures.create_functioncode_with(name="WAN", slug="wan")
        cls.device = create_test_device(name="integration-device")
        cls.other_device = create_test_device(name="integration-device-2")
        user_model = get_user_model()
        if not user_model.objects.filter(is_superuser=True).exists():
            user_model.objects.create_superuser("integration-user", "integration-user@example.com", "password")
        cls.user = user_model.objects.filter(is_superuser=True).first()

    def setUp(self):
        self.client.force_login(self.user)

    def test_set_and_get_device_function_code(self):
        set_device_function_code(self.device, self.function_code)
        self.assertEqual(get_device_function_code(self.device), self.function_code)

    def test_assign_devices_to_function_code(self):
        assign_devices_to_function_code(self.function_code, [self.device, self.other_device])
        self.assertEqual(get_device_function_code(self.device), self.function_code)
        self.assertEqual(get_device_function_code(self.other_device), self.function_code)

    def test_unassign_devices(self):
        assign_devices_to_function_code(self.function_code, [self.device, self.other_device])
        unassign_devices([self.device])
        self.assertIsNone(get_device_function_code(self.device))
        self.assertEqual(get_device_function_code(self.other_device), self.function_code)

    def test_device_filter_extension_field_prefix(self):
        self.assertIn("nautobot_function_codes_function_code", DeviceFilterExtension.filterset_fields)
        self.assertIn("nautobot_function_codes_has_function_code", DeviceFilterExtension.filterset_fields)

    def test_device_has_function_code_filter(self):
        set_device_function_code(self.device, self.function_code)
        assigned = Device.objects.filter(**{"function_code_assignment__function_code__isnull": False})
        unassigned = Device.objects.filter(**{"function_code_assignment__function_code__isnull": True})
        self.assertIn(self.device, assigned)
        self.assertIn(self.other_device, unassigned)

    def test_device_set_function_code_view_updates_assignment(self):
        url = reverse(
            "plugins:nautobot_function_codes:device_set_function_code",
            kwargs={"pk": self.device.pk},
        )
        response = self.client.post(url, {"function_code": str(self.function_code.pk)})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_device_function_code(self.device), self.function_code)

    def test_device_set_function_code_view_clears_assignment(self):
        set_device_function_code(self.device, self.function_code)
        url = reverse(
            "plugins:nautobot_function_codes:device_set_function_code",
            kwargs={"pk": self.device.pk},
        )
        response = self.client.post(url, {"function_code": ""})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(get_device_function_code(self.device))

    def test_assignment_deleted_with_device(self):
        set_device_function_code(self.device, self.function_code)
        device_pk = self.device.pk
        self.device.delete()
        self.assertFalse(models.DeviceFunctionCodeAssignment.objects.filter(device_id=device_pk).exists())

    def test_set_device_function_code_rejects_inactive_function_code(self):
        inactive_code = fixtures.create_functioncode_with(name="OLD", slug="old-inactive", is_active=False)
        with self.assertRaises(ValidationError):
            set_device_function_code(self.device, inactive_code)

    def test_assignment_model_clean_rejects_inactive_function_code(self):
        inactive_code = fixtures.create_functioncode_with(name="RET", slug="ret-inactive", is_active=False)
        assignment = models.DeviceFunctionCodeAssignment(device=self.device, function_code=inactive_code)
        with self.assertRaises(ValidationError):
            assignment.full_clean()
