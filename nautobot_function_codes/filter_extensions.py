"""Filter extensions for core Nautobot models."""

import django_filters
from django import forms
from nautobot.apps.filters import FilterExtension, NaturalKeyOrPKMultipleChoiceFilter
from nautobot.apps.forms import DynamicModelMultipleChoiceField

from nautobot_function_codes import models


class DeviceFilterExtension(FilterExtension):
    """Extend Device filtering with Function Code."""

    model = "dcim.device"
    filterset_fields = {
        "nautobot_function_codes_function_code": NaturalKeyOrPKMultipleChoiceFilter(
            field_name="function_code_assignment__function_code",
            queryset=models.FunctionCode.objects.all(),
            to_field_name="slug",
            label="Function Code",
        ),
        "nautobot_function_codes_has_function_code": django_filters.BooleanFilter(
            field_name="function_code_assignment__function_code",
            lookup_expr="isnull",
            exclude=True,
            label="Has Function Code",
        ),
    }
    filterform_fields = {
        "nautobot_function_codes_function_code": DynamicModelMultipleChoiceField(
            queryset=models.FunctionCode.objects.all(),
            required=False,
            label="Function Code",
        ),
        "nautobot_function_codes_has_function_code": forms.NullBooleanField(
            required=False,
            label="Has Function Code",
        ),
    }


filter_extensions = [DeviceFilterExtension]
