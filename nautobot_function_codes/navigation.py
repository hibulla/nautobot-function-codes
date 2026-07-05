"""Navigation menu items for the Function Codes plugin."""

from nautobot.apps.ui import (
    NavigationWeightChoices,
    NavMenuAddButton,
    NavMenuGroup,
    NavMenuItem,
    NavMenuTab,
)

FUNCTION_CODES_TAB_ICON = "nautobot_function_codes/icons/tag-multiple.svg"

VIEW_FUNCTION_CODE = "nautobot_function_codes.view_functioncode"
VIEW_DEVICE_ASSIGNMENT = "nautobot_function_codes.view_devicefunctioncodeassignment"
ADD_FUNCTION_CODE = "nautobot_function_codes.add_functioncode"
ADD_DEVICE_ASSIGNMENT = "nautobot_function_codes.add_devicefunctioncodeassignment"
CHANGE_DEVICE_ASSIGNMENT = "nautobot_function_codes.change_devicefunctioncodeassignment"

function_code_items = (
    NavMenuItem(
        link="plugins:nautobot_function_codes:functioncode_list",
        name="Function Codes",
        weight=100,
        permissions=[VIEW_FUNCTION_CODE],
        buttons=(
            NavMenuAddButton(
                link="plugins:nautobot_function_codes:functioncode_add",
                permissions=[ADD_FUNCTION_CODE],
            ),
        ),
    ),
    NavMenuItem(
        link="plugins:nautobot_function_codes:devicefunctioncodeassignment_list",
        name="Device Assignments",
        weight=200,
        permissions=[VIEW_DEVICE_ASSIGNMENT],
        buttons=(
            NavMenuAddButton(
                link="plugins:nautobot_function_codes:devicefunctioncodeassignment_add",
                permissions=[ADD_DEVICE_ASSIGNMENT],
            ),
        ),
    ),
    NavMenuItem(
        link="plugins:nautobot_function_codes:coverage_dashboard",
        name="Coverage",
        weight=300,
        permissions=[VIEW_FUNCTION_CODE],
    ),
    NavMenuItem(
        link="plugins:nautobot_function_codes:import_assignments",
        name="Import Assignments",
        weight=400,
        permissions=[CHANGE_DEVICE_ASSIGNMENT],
    ),
    NavMenuItem(
        link="plugins:nautobot_function_codes:devicefunctioncodeassignment_clear",
        name="Clear Assignments",
        weight=500,
        permissions=[CHANGE_DEVICE_ASSIGNMENT],
    ),
)

menu_items = (
    NavMenuTab(
        name="Function Codes",
        weight=NavigationWeightChoices.ORGANIZATION + 10,
        icon=FUNCTION_CODES_TAB_ICON,
        permissions=[VIEW_FUNCTION_CODE],
        groups=(
            NavMenuGroup(
                name="Function Codes",
                weight=100,
                items=function_code_items,
            ),
        ),
    ),
)
