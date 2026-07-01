"""Filter extensions for core Nautobot models."""

from nautobot.apps.filters import NaturalKeyOrPKMultipleChoiceFilter, PluginFilterExtension
from nautobot.apps.forms import DynamicModelMultipleChoiceField

from nautobot_function_codes import models


class DeviceFilterExtension(PluginFilterExtension):
    """Extend Device filtering with Function Code."""

    model = "dcim.device"
    filterset_fields = {
        "nautobot_function_codes_function_code": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="function_code_assignment__function_code",
            queryset=models.FunctionCode.objects.all(),
            to_field_name="slug",
            label="Function Code",
        ),
    }
    filterform_fields = {
        "nautobot_function_codes_function_code": DynamicModelMultipleChoiceField(
            queryset=models.FunctionCode.objects.all(),
            required=False,
            label="Function Code",
        ),
    }


filter_extensions = [DeviceFilterExtension]
