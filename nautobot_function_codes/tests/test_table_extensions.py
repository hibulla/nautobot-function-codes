"""Tests for Device table extensions."""

from nautobot.apps.testing import TestCase
from nautobot.dcim.models import Device

from nautobot_function_codes.table_extensions import DeviceFunctionCodeTableExtension
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device
from nautobot_function_codes.utils import set_device_function_code


class DeviceFunctionCodeTableExtensionTest(TestCase):
    """Test the Device list table extension."""

    @classmethod
    def setUpTestData(cls):
        cls.function_code = fixtures.create_functioncode_with(name="ACC", slug="acc-table")
        cls.device = create_test_device(name="table-device")
        set_device_function_code(cls.device, cls.function_code)

    def test_alter_queryset_prefetches_assignment(self):
        queryset = DeviceFunctionCodeTableExtension.alter_queryset(Device.objects.all())
        device = queryset.get(pk=self.device.pk)
        self.assertEqual(device.function_code_assignment.function_code.name, "ACC")

    def test_table_extension_registers_column(self):
        self.assertIn(
            "nautobot_function_codes_function_code",
            DeviceFunctionCodeTableExtension.table_columns,
        )
        self.assertIn(
            "nautobot_function_codes_function_code",
            DeviceFunctionCodeTableExtension.add_to_default_columns,
        )
