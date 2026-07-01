"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:nautobot_function_codes:functioncode_list",
        name="Function Codes",
        permissions=["nautobot_function_codes.view_functioncode"],
        buttons=(
            NavMenuAddButton(
                link="plugins:nautobot_function_codes:functioncode_add",
                permissions=["nautobot_function_codes.add_functioncode"],
            ),
        ),
    ),
)

menu_items = (
    NavMenuTab(
        name="Function Codes",
        groups=(NavMenuGroup(name="Function Codes", items=tuple(items)),),
    ),
)
