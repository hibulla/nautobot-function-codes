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
        "is_active": True,
    }
    update_data = {
        "name": "Test 2",
        "slug": "test-2",
        "description": "Updated model",
        "is_active": False,
    }

    @classmethod
    def setUpTestData(cls):
        fixtures.create_functioncode()
