"""Nautobot jobs for Function Code assignment management."""

from nautobot.apps.jobs import register_jobs
from nautobot.extras.jobs import BooleanVar, FileVar, Job

from nautobot_function_codes.services.coverage import get_audit_report
from nautobot_function_codes.services.import_assignments import import_assignments_from_csv

IMPORT_ROW_LOG_LIMIT = 1000


class AuditFunctionCodeAssignments(Job):
    """Report devices without Function Codes and inactive assignments."""

    include_inactive_codes = BooleanVar(
        description="Include assignments to inactive Function Codes in the report.",
        default=True,
    )

    class Meta:
        """Meta attributes."""

        name = "Audit Function Code Assignments"
        description = "Report devices without Function Codes and inactive assignments."
        has_sensitive_variables = False

    def run(self, *, include_inactive_codes):
        """Generate and log the audit report."""
        report = get_audit_report(self.user, include_inactive=include_inactive_codes)
        for line in report.log_lines:
            self.logger.info(line)
        self.logger.info(report.summary)
        return report.summary


class ImportFunctionCodeAssignments(Job):
    """Import device Function Code assignments from a CSV file."""

    csv_file = FileVar(description="CSV file with columns: device, function_code")
    dry_run = BooleanVar(description="Validate the file without saving changes.", default=False)

    class Meta:
        """Meta attributes."""

        name = "Import Function Code Assignments"
        description = "Import device Function Code assignments from a CSV file."
        has_sensitive_variables = False

    def run(self, *, csv_file, dry_run):
        """Process the uploaded CSV file."""
        try:
            result = import_assignments_from_csv(csv_file, self.user, dry_run=dry_run)
        except ValueError as exc:
            self.logger.error(str(exc))
            raise

        for row in result.rows[:IMPORT_ROW_LOG_LIMIT]:
            self.logger.info(
                "Row %s [%s] device=%s function_code=%s: %s",
                row.row_number,
                row.status,
                row.device_name,
                row.function_code_slug,
                row.message,
            )
        if len(result.rows) > IMPORT_ROW_LOG_LIMIT:
            self.logger.info(
                "Skipped logging %s additional import row result(s).", len(result.rows) - IMPORT_ROW_LOG_LIMIT
            )

        if result.errors:
            self.logger.warning(result.summary)
        else:
            self.logger.info(result.summary)
        return result.summary


jobs = [AuditFunctionCodeAssignments, ImportFunctionCodeAssignments]
register_jobs(*jobs)
