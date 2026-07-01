"""Device integration tests."""

from nautobot.apps.testing import TestCase

from nautobot_function_codes import models
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device
from nautobot_function_codes.utils import get_device_function_code, set_device_function_code


class DeviceFunctionCodeIntegrationTest(TestCase):
    """Test Device assignment helpers and filter extension field naming."""

    @classmethod
    def setUpTestData(cls):
        cls.function_code = fixtures.create_functioncode_with(name="DIS", slug="dis")
        cls.device = create_test_device(name="integration-device")

    def test_set_and_get_device_function_code(self):
        set_device_function_code(self.device, self.function_code)
        self.assertEqual(get_device_function_code(self.device), self.function_code)

    def test_device_filter_extension_field_prefix(self):
        from nautobot_function_codes.filter_extensions import DeviceFilterExtension

        self.assertIn("nautobot_function_codes_function_code", DeviceFilterExtension.filterset_fields)

    def test_assignment_deleted_with_device(self):
        set_device_function_code(self.device, self.function_code)
        device_pk = self.device.pk
        self.device.delete()
        self.assertFalse(models.DeviceFunctionCodeAssignment.objects.filter(device_id=device_pk).exists())
