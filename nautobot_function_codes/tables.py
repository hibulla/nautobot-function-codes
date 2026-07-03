"""Tables for nautobot_function_codes."""

import django_tables2 as tables
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from nautobot.apps.tables import BaseTable, BooleanColumn, ButtonsColumn, ColorColumn, LinkedCountColumn, ToggleColumn
from nautobot.apps.ui import ObjectsTablePanel
from nautobot.core.templatetags import helpers

from nautobot_function_codes import models


class DeviceAssignmentCountColumn(LinkedCountColumn):
    """Always render a linked count badge, even when only one device is assigned."""

    def render(self, *, bound_column, record, value):
        url = reverse(self.viewname, kwargs=self.view_kwargs)
        if self.url_params:
            url += "?" + urlencode(
                {k: (getattr(record, v) or settings.FILTERS_NULL_CHOICE_VALUE) for k, v in self.url_params.items()}
            )
        if value:
            return format_html('<a href="{}" class="badge bg-primary">{}</a>', url, value)
        return helpers.placeholder(value)


class FunctionCodeTable(BaseTable):
    """Table for FunctionCode list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    description = tables.Column()
    color = ColorColumn()
    is_active = BooleanColumn()
    device_count = DeviceAssignmentCountColumn(
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
            "description",
            "color",
            "is_active",
            "device_count",
            "actions",
        )
        default_columns = (
            "pk",
            "name",
            "description",
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
    add_button_route = None
