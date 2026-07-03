"""Filtering for nautobot_function_codes."""

from nautobot.apps.filters import (
    NameSearchFilterSet,
    NaturalKeyOrPKMultipleChoiceFilter,
    NautobotFilterSet,
    SearchFilter,
)
from nautobot.dcim.models import Device

from nautobot_function_codes import models


class FunctionCodeFilterSet(NameSearchFilterSet, NautobotFilterSet):
    """FilterSet for FunctionCode."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "slug": "icontains",
            "description": "icontains",
        },
    )

    class Meta:
        """Meta attributes."""

        model = models.FunctionCode
        fields = "__all__"


class DeviceFunctionCodeAssignmentFilterSet(NautobotFilterSet):
    """FilterSet for DeviceFunctionCodeAssignment."""

    device = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="device",
        queryset=Device.objects.all(),
        to_field_name="name",
    )
    function_code = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="function_code",
        queryset=models.FunctionCode.objects.all(),
        to_field_name="slug",
    )

    class Meta:
        """Meta attributes."""

        model = models.DeviceFunctionCodeAssignment
        fields = "__all__"
