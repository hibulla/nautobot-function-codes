"""Navigation tests."""

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase

from nautobot_function_codes.navigation import FUNCTION_CODES_TAB_ICON, menu_items


class NavigationTest(SimpleTestCase):
    """Test plugin navigation configuration."""

    def test_tab_icon_uses_nautobot_icon_name(self):
        """Ensure Nautobot can resolve the plugin tab icon."""
        tab = menu_items[0]

        self.assertEqual(tab.icon, FUNCTION_CODES_TAB_ICON)
        self.assertEqual(FUNCTION_CODES_TAB_ICON, "transform")
        self.assertIsNotNone(finders.find(f"nautobot-icons/{FUNCTION_CODES_TAB_ICON}.svg"))
