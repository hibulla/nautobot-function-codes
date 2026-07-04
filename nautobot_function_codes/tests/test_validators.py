"""Tests for Function Code assignment validation."""

from django.core.exceptions import ValidationError
from nautobot.apps.testing import APIViewTestCases, TestCase

from nautobot_function_codes import models
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device
from nautobot_function_codes.validators import validate_function_code_for_assignment


class ValidateFunctionCodeForAssignmentTest(TestCase):
    """Test the shared assignment validator."""

    @classmethod
    def setUpTestData(cls):
        cls.active_code = fixtures.create_functioncode_with(name="ACT", slug="act-validate")
        cls.inactive_code = fixtures.create_functioncode_with(name="OLD", slug="old-validate", is_active=False)

    def test_allows_active_function_code(self):
        validate_function_code_for_assignment(self.active_code)

    def test_allows_none(self):
        validate_function_code_for_assignment(None)

    def test_rejects_inactive_function_code(self):
        with self.assertRaises(ValidationError):
            validate_function_code_for_assignment(self.inactive_code)


class DeviceFunctionCodeAssignmentAPIValidationTest(APIViewTestCases.APIViewTestCase):
    """Test API rejection of inactive Function Code assignments."""

    model = models.DeviceFunctionCodeAssignment
    choices_fields = ()
    brief_fields = ["id", "url", "display", "device", "function_code"]
    validation_excluded_fields = []

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.active_code = fixtures.create_functioncode_with(name="API-ACT", slug="api-act")
        cls.inactive_code = fixtures.create_functioncode_with(name="API-OLD", slug="api-old", is_active=False)
        cls.device = create_test_device(name="api-validate-device")
        cls.create_data = [
            {
                "device": cls.device.pk,
                "function_code": cls.inactive_code.pk,
            }
        ]

    def test_create_assignment_rejects_inactive_function_code(self):
        self.assertHttpStatus(
            self.client.post(self._get_list_url(), self.create_data[0], format="json", **self.header),
            400,
        )
