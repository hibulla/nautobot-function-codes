"""Test FunctionCode models."""

from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError
from nautobot.apps.testing import ModelTestCases, TestCase

from nautobot_function_codes import models
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device
from nautobot_function_codes.utils import get_device_function_code, set_device_function_code


class TestFunctionCode(ModelTestCases.BaseModelTestCase):
    """Test FunctionCode model."""

    model = models.FunctionCode

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        fixtures.create_functioncode()

    def test_create_functioncode_only_required(self):
        functioncode = models.FunctionCode.objects.create(name="Development", slug="development")
        self.assertEqual(functioncode.name, "Development")
        self.assertEqual(functioncode.description, "")
        self.assertTrue(functioncode.is_active)
        self.assertEqual(str(functioncode), "Development")

    def test_create_functioncode_all_fields_success(self):
        functioncode = models.FunctionCode.objects.create(
            name="Development",
            slug="development-full",
            description="Development Test",
            color="ff0000",
            is_active=False,
        )
        self.assertEqual(functioncode.color, "ff0000")
        self.assertFalse(functioncode.is_active)


class TestDeviceFunctionCodeAssignment(TestCase):
    """Test DeviceFunctionCodeAssignment model."""

    model = models.DeviceFunctionCodeAssignment

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.function_code = fixtures.create_functioncode_with(name="WAN", slug="wan")
        cls.device = create_test_device(name="device-1")

    def test_assignment_one_to_one(self):
        set_device_function_code(self.device, self.function_code)
        assignment = models.DeviceFunctionCodeAssignment.objects.get(device=self.device)
        self.assertEqual(assignment.function_code, self.function_code)
        self.assertEqual(get_device_function_code(self.device), self.function_code)

    def test_assignment_update(self):
        other_code = fixtures.create_functioncode_with(name="ACC", slug="acc")
        set_device_function_code(self.device, self.function_code)
        set_device_function_code(self.device, other_code)
        self.assertEqual(models.DeviceFunctionCodeAssignment.objects.filter(device=self.device).count(), 1)
        self.assertEqual(get_device_function_code(self.device), other_code)

    def test_assignment_clear(self):
        set_device_function_code(self.device, self.function_code)
        set_device_function_code(self.device, None)
        assignment = models.DeviceFunctionCodeAssignment.objects.get(device=self.device)
        self.assertIsNone(assignment.function_code)

    def test_protect_function_code_on_delete(self):
        set_device_function_code(self.device, self.function_code)
        with self.assertRaises(ProtectedError):
            self.function_code.delete()

    def test_duplicate_assignment_not_allowed(self):
        models.DeviceFunctionCodeAssignment.objects.create(device=self.device, function_code=self.function_code)
        with self.assertRaises(IntegrityError):
            models.DeviceFunctionCodeAssignment.objects.create(device=self.device, function_code=self.function_code)
