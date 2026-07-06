"""CSV import logic for device Function Code assignments."""

import csv
import io
import uuid
from dataclasses import dataclass, field

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from nautobot.dcim.models import Device

from nautobot_function_codes import models
from nautobot_function_codes.utils import set_device_function_code
from nautobot_function_codes.validators import validate_function_code_for_assignment

REQUIRED_COLUMNS = ("device", "function_code")
MAX_CSV_ROWS = 50000


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
        return f"{prefix}updated={self.updated}, cleared={self.cleared}, skipped={self.skipped}, errors={self.errors}"


@dataclass
class ImportLookups:
    """Preloaded lookup maps for a CSV import."""

    devices_by_pk: dict
    devices_by_name: dict
    function_codes_by_slug: dict
    function_codes_by_name: dict


def _parse_csv(text, *, max_rows=MAX_CSV_ROWS):
    """Parse CSV text into row tuples of line number, device, and function code."""
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
        if len(rows) >= max_rows:
            raise ValueError(f"CSV import is limited to {max_rows} non-empty data rows.")
        rows.append((index, device_value, function_code_value))
    return rows


def _build_device_lookup(parsed_rows, user):
    """Build permission-aware device lookup maps for an import."""
    device_names = set()
    device_uuids = set()
    for _, device_value, _ in parsed_rows:
        if not device_value:
            continue
        try:
            device_uuids.add(uuid.UUID(device_value))
        except (TypeError, ValueError):
            device_names.add(device_value)

    devices = Device.objects.restrict(user, "change").select_related("function_code_assignment__function_code")
    query = Q()
    if device_uuids:
        query |= Q(pk__in=device_uuids)
    if device_names:
        query |= Q(name__in=device_names)
    if not query:
        return {}, {}

    by_pk = {}
    by_name = {}
    for device in devices.filter(query).order_by("name", "pk"):
        by_pk[device.pk] = device
        by_name.setdefault(device.name, device)
    return by_pk, by_name


def _build_function_code_lookup(parsed_rows, user):
    """Build permission-aware Function Code lookup maps for an import."""
    values = {function_code_value for _, _, function_code_value in parsed_rows if function_code_value}
    if not values:
        return {}, {}

    function_codes = models.FunctionCode.objects.restrict(user, "view").filter(Q(slug__in=values) | Q(name__in=values))
    by_slug = {}
    by_name = {}
    for function_code in function_codes:
        by_slug[function_code.slug] = function_code
        by_name[function_code.name] = function_code
    return by_slug, by_name


def _resolve_device_from_lookup(device_value, devices_by_pk, devices_by_name):
    """Look up a device by UUID or name from preloaded maps."""
    try:
        device_uuid = uuid.UUID(device_value)
    except (TypeError, ValueError):
        device_uuid = None

    if device_uuid is not None:
        device = devices_by_pk.get(device_uuid)
        if device is not None:
            return device
    return devices_by_name.get(device_value)


def _resolve_function_code_from_lookup(function_code_value, function_codes_by_slug, function_codes_by_name):
    """Look up and validate a Function Code from preloaded maps."""
    if not function_code_value:
        return None

    function_code = function_codes_by_slug.get(function_code_value) or function_codes_by_name.get(function_code_value)
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


def _add_import_row(result, row):
    """Append a row result to the import result."""
    result.rows.append(row)


def _process_import_row(row, lookups, result, *, dry_run):
    """Process one parsed CSV row."""
    row_number, device_value, function_code_value = row
    if not device_value:
        result.errors += 1
        _add_import_row(
            result,
            ImportRowResult(
                row_number=row_number,
                device_name=device_value,
                function_code_slug=function_code_value,
                status="error",
                message="Device value is required.",
            ),
        )
        return

    device = _resolve_device_from_lookup(device_value, lookups.devices_by_pk, lookups.devices_by_name)
    if device is None:
        result.errors += 1
        _add_import_row(
            result,
            ImportRowResult(
                row_number=row_number,
                device_name=device_value,
                function_code_slug=function_code_value,
                status="error",
                message=f"Device '{device_value}' was not found or is not permitted.",
            ),
        )
        return

    try:
        function_code = _resolve_function_code_from_lookup(
            function_code_value,
            lookups.function_codes_by_slug,
            lookups.function_codes_by_name,
        )
    except ValueError as exc:
        result.errors += 1
        _add_import_row(
            result,
            ImportRowResult(
                row_number=row_number,
                device_name=device.name,
                function_code_slug=function_code_value,
                status="error",
                message=str(exc),
            ),
        )
        return

    current_function_code = getattr(
        getattr(device, "function_code_assignment", None),
        "function_code",
        None,
    )
    if current_function_code == function_code:
        result.skipped += 1
        _add_import_row(
            result,
            ImportRowResult(
                row_number=row_number,
                device_name=device.name,
                function_code_slug=function_code_value,
                status="skipped",
                message="Assignment already matches.",
            ),
        )
        return

    if not dry_run:
        with transaction.atomic():
            set_device_function_code(device, function_code)

    if function_code is None:
        result.cleared += 1
        _add_import_row(
            result,
            ImportRowResult(
                row_number=row_number,
                device_name=device.name,
                function_code_slug=function_code_value,
                status="cleared",
                message="Assignment cleared.",
            ),
        )
    else:
        result.updated += 1
        _add_import_row(
            result,
            ImportRowResult(
                row_number=row_number,
                device_name=device.name,
                function_code_slug=function_code_value,
                status="updated",
                message=f"Assigned to {function_code.name}.",
            ),
        )


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
    lookups = ImportLookups(
        *_build_device_lookup(parsed_rows, user),
        *_build_function_code_lookup(parsed_rows, user),
    )

    for row in parsed_rows:
        _process_import_row(
            row,
            lookups,
            result,
            dry_run=dry_run,
        )

    return result
