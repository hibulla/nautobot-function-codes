"""Shared helpers for plugin tests."""

from nautobot.dcim.models import Device, DeviceType, Location, LocationType, Manufacturer
from nautobot.extras.models import Role, Status


def create_test_device(name="test-device"):
    """Create a minimal valid Device for plugin tests."""
    manufacturer, _ = Manufacturer.objects.get_or_create(
        name="Test Manufacturer",
        defaults={"slug": "test-manufacturer"},
    )
    device_type, _ = DeviceType.objects.get_or_create(
        manufacturer=manufacturer,
        model="Test Model",
        defaults={"slug": "test-model"},
    )
    location_type, _ = LocationType.objects.get_or_create(
        name="Site",
        defaults={"slug": "site"},
    )
    location_status = Status.objects.get_for_model(Location).first()
    location, _ = Location.objects.get_or_create(
        name="Test Site",
        defaults={
            "slug": "test-site",
            "location_type": location_type,
            "status": location_status,
        },
    )
    device_status = Status.objects.get_for_model(Device).first()
    device_role = Role.objects.get_for_model(Device).first()
    return Device.objects.create(
        name=name,
        status=device_status,
        role=device_role,
        device_type=device_type,
        location=location,
    )
