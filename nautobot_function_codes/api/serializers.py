"""API serializers for nautobot_function_codes."""

from rest_framework import serializers

from nautobot.apps.api import NautobotModelSerializer

from nautobot_function_codes import models


class FunctionCodeSerializer(NautobotModelSerializer):
    """FunctionCode REST API serializer."""

    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.FunctionCode
        fields = [
            "id",
            "url",
            "display",
            "name",
            "slug",
            "description",
            "color",
            "is_active",
            "device_count",
            "created",
            "last_updated",
            "notes_url",
            "custom_fields",
        ]


class DeviceFunctionCodeAssignmentSerializer(NautobotModelSerializer):
    """DeviceFunctionCodeAssignment REST API serializer."""

    class Meta:
        model = models.DeviceFunctionCodeAssignment
        fields = [
            "id",
            "url",
            "display",
            "device",
            "function_code",
            "created",
            "last_updated",
        ]
