"""API serializers for nautobot_function_codes."""

from nautobot.apps.api import NautobotModelSerializer
from rest_framework import serializers

from nautobot_function_codes import models


class FunctionCodeSerializer(NautobotModelSerializer):
    """Serialize FunctionCode records for the REST API."""

    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta attributes."""

        model = models.FunctionCode
        fields = "__all__"


class DeviceFunctionCodeAssignmentSerializer(NautobotModelSerializer):
    """Serialize DeviceFunctionCodeAssignment records for the REST API."""

    class Meta:
        """Meta attributes."""

        model = models.DeviceFunctionCodeAssignment
        fields = "__all__"
