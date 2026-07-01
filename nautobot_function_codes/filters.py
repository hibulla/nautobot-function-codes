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
    is_active = django_filters.BooleanFilter()
    name = django_filters.CharFilter()
    slug = django_filters.CharFilter()

    class Meta:
        """Meta attributes."""

        model = models.FunctionCode
        fields = ["id", "name", "slug", "description", "color", "is_active", "created", "last_updated"]


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
        fields = ["id", "device_id", "function_code", "created", "last_updated"]
