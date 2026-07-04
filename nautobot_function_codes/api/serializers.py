"""API serializers for nautobot_function_codes."""

from nautobot.apps.api import NautobotModelSerializer, ValidatedModelSerializer
from rest_framework import serializers

from nautobot_function_codes import models
from nautobot_function_codes.validators import validate_function_code_for_assignment


class FunctionCodeSerializer(NautobotModelSerializer):
    """Serialize FunctionCode records for the REST API."""

    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta attributes."""

        model = models.FunctionCode
        fields = "__all__"


class DeviceFunctionCodeAssignmentSerializer(ValidatedModelSerializer):
    """Serialize DeviceFunctionCodeAssignment records for the REST API."""

    def validate_function_code(self, value):
        """Reject inactive Function Codes for new assignments."""
        validate_function_code_for_assignment(value)
        return value

    class Meta:
        """Meta attributes."""

        model = models.DeviceFunctionCodeAssignment
        fields = [
            "id",
            "url",
            "display",
            "natural_slug",
            "device",
            "function_code",
        ]
