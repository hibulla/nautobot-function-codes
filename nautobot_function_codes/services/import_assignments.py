"""CSV import logic for device Function Code assignments."""

import csv
import io
import uuid
from dataclasses import dataclass, field

from django.core.exceptions import ValidationError
from django.db import transaction
from nautobot.dcim.models import Device

from nautobot_function_codes import models
from nautobot_function_codes.utils import set_device_function_code
from nautobot_function_codes.validators import validate_function_code_for_assignment

REQUIRED_COLUMNS = ("device", "function_code")


@dataclass
class ImportRowResult:
    """Result for a single CSV row."""

    row_number: int
    device_name: str
    function_code_slug: str
    status: str
    message: str = ""


@dataclass
class ImportAssignmentsResult:
    """Aggregate CSV import result."""

    dry_run: bool = False
    updated: int = 0
    cleared: int = 0
    skipped: int = 0
    errors: int = 0
    rows: list[ImportRowResult] = field(default_factory=list)

    @property
    def summary(self):
        """Return a human-readable summary."""
        prefix = "Dry run: " if self.dry_run else ""
        return (
            f"{prefix}updated={self.updated}, cleared={self.cleared}, "
            f"skipped={self.skipped}, errors={self.errors}"
        )


def _parse_csv(text):
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV file is missing a header row.")
    normalized_headers = {header.strip().lower(): header for header in reader.fieldnames if header}
    missing = [column for column in REQUIRED_COLUMNS if column not in normalized_headers]
    if missing:
        raise ValueError(f"CSV is missing required column(s): {', '.join(missing)}")

    rows = []
    for index, row in enumerate(reader, start=2):
        device_value = (row.get(normalized_headers["device"]) or "").strip()
        function_code_value = (row.get(normalized_headers["function_code"]) or "").strip()
        if not device_value and not function_code_value:
            continue
        rows.append((index, device_value, function_code_value))
    return rows


def _resolve_device(device_value, user):
    devices = Device.objects.restrict(user, "change")
    try:
        device_uuid = uuid.UUID(device_value)
    except (TypeError, ValueError):
        device_uuid = None

    if device_uuid is not None:
        device = devices.filter(pk=device_uuid).first()
        if device is not None:
            return device

    return devices.filter(name=device_value).first()


def _resolve_function_code(function_code_value, user):
    if not function_code_value:
        return None

    function_codes = models.FunctionCode.objects.restrict(user, "view")
    function_code = function_codes.filter(slug=function_code_value).first()
    if function_code is None:
        function_code = function_codes.filter(name=function_code_value).first()
    if function_code is None:
        raise ValueError(f"Function Code '{function_code_value}' was not found.")

    try:
        validate_function_code_for_assignment(function_code)
    except ValidationError as exc:
        message = exc.message_dict.get("function_code", exc.messages)
        if isinstance(message, list):
            message = message[0]
        raise ValueError(message) from exc

    return function_code


def import_assignments_from_csv(csv_file, user, *, dry_run=False):
    """Import or validate device assignments from a CSV upload."""
    if hasattr(csv_file, "read"):
        raw = csv_file.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8-sig")
    else:
        raw = str(csv_file)

    parsed_rows = _parse_csv(raw)
    result = ImportAssignmentsResult(dry_run=dry_run)

    for row_number, device_value, function_code_value in parsed_rows:
        if not device_value:
            result.errors += 1
            result.rows.append(
                ImportRowResult(
                    row_number=row_number,
                    device_name=device_value,
                    function_code_slug=function_code_value,
                    status="error",
                    message="Device value is required.",
                )
            )
            continue

        device = _resolve_device(device_value, user)
        if device is None:
            result.errors += 1
            result.rows.append(
                ImportRowResult(
                    row_number=row_number,
                    device_name=device_value,
                    function_code_slug=function_code_value,
                    status="error",
                    message=f"Device '{device_value}' was not found or is not permitted.",
                )
            )
            continue

        try:
            function_code = _resolve_function_code(function_code_value, user)
        except ValueError as exc:
            result.errors += 1
            result.rows.append(
                ImportRowResult(
                    row_number=row_number,
                    device_name=device.name,
                    function_code_slug=function_code_value,
                    status="error",
                    message=str(exc),
                )
            )
            continue

        current_function_code = getattr(
            getattr(device, "function_code_assignment", None),
            "function_code",
            None,
        )
        if current_function_code == function_code:
            result.skipped += 1
            result.rows.append(
                ImportRowResult(
                    row_number=row_number,
                    device_name=device.name,
                    function_code_slug=function_code_value,
                    status="skipped",
                    message="Assignment already matches.",
                )
            )
            continue

        if not dry_run:
            with transaction.atomic():
                set_device_function_code(device, function_code)

        if function_code is None:
            result.cleared += 1
            status = "cleared"
            message = "Assignment cleared."
        else:
            result.updated += 1
            status = "updated"
            message = f"Assigned to {function_code.name}."

        result.rows.append(
            ImportRowResult(
                row_number=row_number,
                device_name=device.name,
                function_code_slug=function_code_value,
                status=status,
                message=message,
            )
        )

    return result
