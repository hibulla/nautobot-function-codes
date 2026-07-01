"""Create fixtures for tests."""

from nautobot_function_codes.models import FunctionCode


def create_functioncode():
    """Create FunctionCode records for tests."""
    FunctionCode.objects.create(name="Test One", slug="test-one")
    FunctionCode.objects.create(name="Test Two", slug="test-two")
    FunctionCode.objects.create(name="Test Three", slug="test-three")


def create_functioncode_with(**kwargs):
    """Create a single FunctionCode with optional overrides."""
    defaults = {
        "name": "Example Code",
        "slug": "example-code",
        "description": "Example description",
        "is_active": True,
    }
    defaults.update(kwargs)
    return FunctionCode.objects.create(**defaults)
