"""Navigation tests."""

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase

from nautobot_function_codes.navigation import FUNCTION_CODES_TAB_ICON, menu_items


class NavigationTest(SimpleTestCase):
    """Test plugin navigation configuration."""

    def test_tab_icon_uses_static_relative_path(self):
        """Ensure Nautobot can resolve the plugin tab icon."""
        tab = menu_items[0]

        self.assertEqual(tab.icon, FUNCTION_CODES_TAB_ICON)
        self.assertEqual(FUNCTION_CODES_TAB_ICON, "nautobot_function_codes/icons/tag-multiple.svg")
        self.assertIsNotNone(finders.find(FUNCTION_CODES_TAB_ICON))
