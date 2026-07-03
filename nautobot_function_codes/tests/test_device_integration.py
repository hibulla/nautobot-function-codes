"""Device integration tests."""

from nautobot.apps.testing import TestCase

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

    def test_assignment_deleted_with_device(self):
        set_device_function_code(self.device, self.function_code)
        device_pk = self.device.pk
        self.device.delete()
        self.assertFalse(models.DeviceFunctionCodeAssignment.objects.filter(device_id=device_pk).exists())
