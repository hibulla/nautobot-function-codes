"""Tables for nautobot_function_codes."""

import django_tables2 as tables
from nautobot.apps.tables import BaseTable, BooleanColumn, ButtonsColumn, ColorColumn, LinkedCountColumn, ToggleColumn
from nautobot.apps.ui import ObjectsTablePanel

from nautobot_function_codes import models


class FunctionCodeTable(BaseTable):
    """Table for FunctionCode list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    slug = tables.Column()
    color = ColorColumn()
    is_active = BooleanColumn()
    device_count = LinkedCountColumn(
        viewname="plugins:nautobot_function_codes:devicefunctioncodeassignment_list",
        url_params={"function_code": "slug"},
        verbose_name="Devices",
    )
    actions = ButtonsColumn(models.FunctionCode, pk_field="pk")

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.FunctionCode
        fields = (
            "pk",
            "name",
            "slug",
            "description",
            "color",
            "is_active",
            "device_count",
            "actions",
        )
        default_columns = (
            "pk",
            "name",
            "slug",
            "color",
            "is_active",
            "device_count",
            "actions",
        )


class DeviceFunctionCodeAssignmentTable(BaseTable):
    """Table for Device Function Code assignment list views."""

    pk = ToggleColumn()
    device = tables.Column(linkify=True, order_by=("device__name",))
    function_code = tables.Column(linkify=True, order_by=("function_code__name",))
    actions = ButtonsColumn(models.DeviceFunctionCodeAssignment, pk_field="pk")

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.DeviceFunctionCodeAssignment
        fields = (
            "pk",
            "device",
            "function_code",
            "actions",
        )
        default_columns = (
            "pk",
            "device",
            "function_code",
            "actions",
        )


class FunctionCodeAssignedDevicesPanel(ObjectsTablePanel):
    """Detail panel listing devices assigned to a Function Code."""

    label = "Assigned Devices"
    table_class = DeviceFunctionCodeAssignmentTable
    table_attribute = "device_assignments"
    related_field_name = "function_code"
    exclude_columns = ["function_code"]
    add_button_route = "plugins:nautobot_function_codes:devicefunctioncodeassignment_add"
