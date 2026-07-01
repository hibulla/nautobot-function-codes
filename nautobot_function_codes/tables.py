"""Tables for nautobot_function_codes."""

import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html

from nautobot.apps.tables import BaseTable, BooleanColumn, ButtonsColumn, ColorColumn, LinkedCountColumn, ToggleColumn

from nautobot_function_codes import models


class FunctionCodeTable(BaseTable):
    """Table for FunctionCode list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    slug = tables.Column()
    color = ColorColumn()
    is_active = BooleanColumn()
    device_count = LinkedCountColumn(
        viewname="dcim:device_list",
        url_params={"nautobot_function_codes_function_code": "slug"},
        verbose_name="Devices",
    )
    actions = ButtonsColumn(models.FunctionCode, pk_field="pk")

    class Meta(BaseTable.Meta):
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


class DeviceFunctionCodeColumn(tables.Column):
    """Custom column rendering Function Code on Device list views."""

    def render(self, record, value):
        function_code = value
        if function_code is None:
            return format_html('<span class="text-muted">&mdash;</span>')
        url = reverse("plugins:nautobot_function_codes:functioncode", kwargs={"pk": function_code.pk})
        label = format_html(
            '<span class="badge" style="background-color: {};">&nbsp;</span> {}',
            function_code.color,
            function_code.name,
        )
        return format_html('<a href="{}">{}</a>', url, label)
