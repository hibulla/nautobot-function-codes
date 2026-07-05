"""Utility helpers for device Function Code assignment."""

from django.db import transaction

from nautobot_function_codes.debug_utils import debug_log
from nautobot_function_codes.models import DeviceFunctionCodeAssignment, FunctionCode
from nautobot_function_codes.validators import validate_function_code_for_assignment


def get_device_function_code(device):
    """Return the FunctionCode assigned to a device, if any."""
    assignment = (
        DeviceFunctionCodeAssignment.objects.select_related("function_code").filter(device_id=device.pk).first()
    )
    if assignment is None:
        return None
    return assignment.function_code


def get_device_function_code_link(record):
    """Return a link target for a device's assigned Function Code table column."""
    assignment = getattr(record, "function_code_assignment", None)
    if assignment is None or assignment.function_code is None:
        return None
    return assignment.function_code.get_absolute_url()


def set_device_function_code(device, function_code):
    """Create or update the Function Code assignment for a device."""
    if function_code == "":
        function_code = None

    if function_code is not None and not isinstance(function_code, FunctionCode):
        raise TypeError("function_code must be a FunctionCode instance or None")

    validate_function_code_for_assignment(function_code)

    assignment, created = DeviceFunctionCodeAssignment.objects.get_or_create(device=device)
    assignment.function_code = function_code
    assignment.validated_save()
    debug_log(
        "set_device_function_code: device_pk=%s function_code_pk=%s created=%s",
        device.pk,
        getattr(function_code, "pk", None),
        created,
    )
    return assignment


def set_devices_function_code(devices, function_code):
    """Create or update Function Code assignments for multiple devices."""
    if function_code == "":
        function_code = None

    if function_code is not None and not isinstance(function_code, FunctionCode):
        raise TypeError("function_code must be a FunctionCode instance or None")

    validate_function_code_for_assignment(function_code)

    devices = list(devices)
    existing_assignments = {
        assignment.device_id: assignment
        for assignment in DeviceFunctionCodeAssignment.objects.filter(device_id__in=[device.pk for device in devices])
    }

    assignments = []
    with transaction.atomic():
        for device in devices:
            assignment = existing_assignments.get(device.pk)
            created = assignment is None
            if created:
                assignment = DeviceFunctionCodeAssignment(device=device)
            assignment.function_code = function_code
            assignment.validated_save()
            assignments.append(assignment)
            debug_log(
                "set_devices_function_code: device_pk=%s function_code_pk=%s created=%s",
                device.pk,
                getattr(function_code, "pk", None),
                created,
            )
    return assignments


def assign_devices_to_function_code(function_code, devices):
    """Assign multiple devices to the same Function Code."""
    return set_devices_function_code(devices, function_code)


def unassign_devices(devices):
    """Clear Function Code assignments for the given devices."""
    return set_devices_function_code(devices, None)
