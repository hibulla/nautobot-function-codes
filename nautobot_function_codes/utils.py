"""Utility helpers for device Function Code assignment."""

from nautobot_function_codes.models import DeviceFunctionCodeAssignment, FunctionCode


def get_device_function_code(device):
    """Return the FunctionCode assigned to a device, if any."""
    try:
        assignment = device.function_code_assignment
    except DeviceFunctionCodeAssignment.DoesNotExist:
        return None
    return assignment.function_code


def set_device_function_code(device, function_code):
    """Create or update the Function Code assignment for a device."""
    if function_code == "":
        function_code = None

    if function_code is not None and not isinstance(function_code, FunctionCode):
        raise TypeError("function_code must be a FunctionCode instance or None")

    assignment, _created = DeviceFunctionCodeAssignment.objects.get_or_create(device=device)
    assignment.function_code = function_code
    assignment.validated_save()
    return assignment
