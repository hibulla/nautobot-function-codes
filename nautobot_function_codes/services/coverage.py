"""Coverage statistics and audit helpers."""

from dataclasses import dataclass, field

from django.db.models import Count, Q
from django.urls import reverse
from nautobot.dcim.models import Device

from nautobot_function_codes import models


@dataclass
class FunctionCodeCoverageRow:
    """Coverage summary for a single Function Code."""

    function_code: models.FunctionCode
    device_count: int
    assignments_url: str


@dataclass
class CoverageStats:
    """Aggregate Function Code assignment coverage."""

    total_devices: int
    assigned_devices: int
    unassigned_devices: int
    function_code_rows: list[FunctionCodeCoverageRow]
    unassigned_devices_url: str


@dataclass
class AuditReport:
    """Audit results for Function Code assignments."""

    summary: str
    log_lines: list[str] = field(default_factory=list)
    unassigned_count: int = 0
    inactive_assignment_count: int = 0


def _device_queryset(user):
    return Device.objects.restrict(user, "view")


def get_coverage_stats(user):
    """Return assignment coverage metrics for the dashboard."""
    devices = _device_queryset(user)
    total_devices = devices.count()
    assigned_devices = devices.filter(function_code_assignment__function_code__isnull=False).count()
    unassigned_devices = total_devices - assigned_devices

    function_codes = (
        models.FunctionCode.objects.restrict(user, "view")
        .annotate(
            device_count=Count(
                "device_assignments",
                filter=Q(device_assignments__function_code__isnull=False),
            )
        )
        .order_by("name")
    )

    rows = [
        FunctionCodeCoverageRow(
            function_code=function_code,
            device_count=function_code.device_count,
            assignments_url=(
                reverse("plugins:nautobot_function_codes:devicefunctioncodeassignment_list")
                + f"?function_code={function_code.slug}"
            ),
        )
        for function_code in function_codes
    ]

    unassigned_devices_url = reverse("dcim:device_list") + "?nautobot_function_codes_has_function_code=false"

    return CoverageStats(
        total_devices=total_devices,
        assigned_devices=assigned_devices,
        unassigned_devices=unassigned_devices,
        function_code_rows=rows,
        unassigned_devices_url=unassigned_devices_url,
    )


def get_audit_report(user, *, include_inactive=True):
    """Build an audit report for Function Code assignment coverage."""
    stats = get_coverage_stats(user)
    log_lines = [
        f"Total devices: {stats.total_devices}",
        f"Devices with Function Code: {stats.assigned_devices}",
        f"Devices without Function Code: {stats.unassigned_devices}",
    ]

    unassigned_devices = (
        _device_queryset(user).filter(function_code_assignment__function_code__isnull=True).order_by("name")[:50]
    )
    for device in unassigned_devices:
        log_lines.append(f"Unassigned device: {device.name} ({device.pk})")
    if stats.unassigned_devices > unassigned_devices.count():
        remaining = stats.unassigned_devices - unassigned_devices.count()
        log_lines.append(f"... and {remaining} more unassigned device(s)")

    inactive_assignment_count = 0
    if include_inactive:
        inactive_assignments = (
            models.DeviceFunctionCodeAssignment.objects.restrict(user, "view")
            .filter(function_code__isnull=False, function_code__is_active=False)
            .select_related("device", "function_code")
            .order_by("device__name")[:50]
        )
        inactive_assignment_count = (
            models.DeviceFunctionCodeAssignment.objects.restrict(user, "view")
            .filter(function_code__isnull=False, function_code__is_active=False)
            .count()
        )
        log_lines.append(f"Assignments to inactive Function Codes: {inactive_assignment_count}")
        for assignment in inactive_assignments:
            log_lines.append(f"Inactive assignment: {assignment.device.name} -> {assignment.function_code.slug}")
        if inactive_assignment_count > inactive_assignments.count():
            remaining = inactive_assignment_count - inactive_assignments.count()
            log_lines.append(f"... and {remaining} more inactive assignment(s)")

    summary = (
        f"Audit complete: {stats.unassigned_devices} unassigned device(s), "
        f"{inactive_assignment_count} inactive assignment(s)"
    )
    return AuditReport(
        summary=summary,
        log_lines=log_lines,
        unassigned_count=stats.unassigned_devices,
        inactive_assignment_count=inactive_assignment_count,
    )
