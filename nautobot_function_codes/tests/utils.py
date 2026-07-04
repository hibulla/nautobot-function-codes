"""Shared helpers for plugin tests."""

from django.contrib.contenttypes.models import ContentType
from nautobot.apps.utils import refresh_job_model_from_job_class
from nautobot.core.celery import register_jobs
from nautobot.dcim.models import Device, DeviceType, Location, LocationType, Manufacturer
from nautobot.extras.models import Job, JobQueue, Role, Status


def get_test_job_model(job_class):
    """Ensure a Job class is registered and has a corresponding Job model row."""
    register_jobs(job_class)
    job_model, _ = refresh_job_model_from_job_class(Job, job_class, JobQueue)
    return job_model


def create_test_device(name="test-device"):
    """Create a minimal valid Device for plugin tests."""
    manufacturer, _ = Manufacturer.objects.get_or_create(name="Test Manufacturer")
    device_type, _ = DeviceType.objects.get_or_create(
        manufacturer=manufacturer,
        model="Test Model",
    )
    location_type, _ = LocationType.objects.get_or_create(name="Site")
    location_status = Status.objects.get_for_model(Location).first()
    location, _ = Location.objects.get_or_create(
        name="Test Site",
        location_type=location_type,
        defaults={"status": location_status},
    )
    device_status = Status.objects.get_for_model(Device).first()
    device_role = Role.objects.get_for_model(Device).first()
    if device_role is None:
        device_role = Role.objects.create(name="Test Device Role", color="9e9e9e")
        device_role.content_types.add(ContentType.objects.get_for_model(Device))
    return Device.objects.create(
        name=name,
        status=device_status,
        role=device_role,
        device_type=device_type,
        location=location,
    )
