"""Tests for Function Code assignment validation."""

from django.core.exceptions import ValidationError
from nautobot.apps.testing import TestCase

from nautobot_function_codes.tests import fixtures
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
