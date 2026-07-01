"""Test FunctionCode forms."""

from django.test import TestCase

from nautobot_function_codes import forms


class FunctionCodeFormTest(TestCase):
    """Test FunctionCode forms."""

    def test_specifying_all_fields_success(self):
        form = forms.FunctionCodeForm(
            data={
                "name": "Development",
                "slug": "development",
                "description": "Development Testing",
                "color": "#9e9e9e",
                "is_active": True,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.FunctionCodeForm(
            data={
                "name": "Development",
                "slug": "development-required",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_functioncode_is_required(self):
        form = forms.FunctionCodeForm(data={"description": "Development Testing", "slug": "missing-name"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])
