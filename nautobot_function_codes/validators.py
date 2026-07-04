"""Validation helpers for nautobot_function_codes."""

from django.core.exceptions import ValidationError


def validate_function_code_for_assignment(function_code):
    """Ensure a Function Code may be assigned to a device."""
    if function_code is not None and not function_code.is_active:
        raise ValidationError(
            {"function_code": f"Function Code '{function_code.name}' is inactive and cannot be assigned."}
        )
