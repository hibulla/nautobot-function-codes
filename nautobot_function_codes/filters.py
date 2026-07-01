"""Filtering for nautobot_function_codes."""

import django_filters
from nautobot.apps.filters import (
    NameSearchFilterSet,
    NaturalKeyOrPKMultipleChoiceFilter,
    NautobotFilterSet,
    SearchFilter,
)

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

    device_id = django_filters.UUIDFilter(field_name="device__id")
    function_code = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="function_code",
        queryset=models.FunctionCode.objects.all(),
        to_field_name="slug",
    )

    class Meta:
        """Meta attributes."""

        model = models.DeviceFunctionCodeAssignment
        fields = "__all__"
