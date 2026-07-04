"""Table extensions for core Nautobot models."""

import django_tables2 as tables
from nautobot.apps.tables import TableExtension

from nautobot_function_codes.utils import get_device_function_code_link


class DeviceFunctionCodeTableExtension(TableExtension):
    """Add Function Code column to the Device list table."""

    model = "dcim.device"
    table_columns = {
        "nautobot_function_codes_function_code": tables.Column(
            accessor="function_code_assignment__function_code__name",
            verbose_name="Function Code",
            order_by=("function_code_assignment__function_code__name",),
            linkify=get_device_function_code_link,
        ),
    }
    add_to_default_columns = ("nautobot_function_codes_function_code",)

    @classmethod
    def alter_queryset(cls, queryset):
        """Prefetch assignment data for the custom column."""
        return queryset.select_related("function_code_assignment__function_code")


table_extensions = [DeviceFunctionCodeTableExtension]
