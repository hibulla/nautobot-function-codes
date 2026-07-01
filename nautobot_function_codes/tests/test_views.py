"""Unit tests for views."""

from nautobot.apps.testing import ViewTestCases

from nautobot_function_codes import models
from nautobot_function_codes.tests import fixtures


class FunctionCodeViewTest(ViewTestCases.OrganizationalObjectViewTestCase):
    """Test the FunctionCode views."""

    model = models.FunctionCode
    bulk_edit_data = {"description": "Bulk edit views", "is_active": True}
    form_data = {
        "name": "Test 1",
        "slug": "test-1",
        "description": "Initial model",
        "color": "9e9e9e",
        "is_active": True,
    }
    update_data = {
        "name": "Test 2",
        "slug": "test-2",
        "description": "Updated model",
        "color": "ff0000",
        "is_active": False,
    }

    @classmethod
    def setUpTestData(cls):
        fixtures.create_functioncode()
