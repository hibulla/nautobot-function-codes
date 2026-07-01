"""API views for nautobot_function_codes."""

from django.db.models import Count
from nautobot.apps.api import NautobotModelViewSet

from nautobot_function_codes import filters, models
from nautobot_function_codes.api import serializers


class FunctionCodeViewSet(NautobotModelViewSet):
    """REST API viewset for FunctionCode."""

    queryset = models.FunctionCode.objects.annotate(device_count=Count("device_assignments"))
    serializer_class = serializers.FunctionCodeSerializer
    filterset_class = filters.FunctionCodeFilterSet


class DeviceFunctionCodeAssignmentViewSet(NautobotModelViewSet):
    """REST API viewset for DeviceFunctionCodeAssignment."""

    queryset = models.DeviceFunctionCodeAssignment.objects.select_related("device", "function_code")
    serializer_class = serializers.DeviceFunctionCodeAssignmentSerializer
    filterset_class = filters.DeviceFunctionCodeAssignmentFilterSet
