"""Run diagnostics for the Nautobot Function Codes plugin."""

from django.core.management.base import BaseCommand

from nautobot_function_codes.debug_utils import is_debug_logging_enabled
from nautobot_function_codes.diagnostics import collect_device_integration_diagnostics


class Command(BaseCommand):
    """Print Device integration diagnostics for troubleshooting."""

    help = "Run Function Codes plugin diagnostics (Device UI integration, URL overrides, optional get_object check)."

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--device-pk",
            dest="device_pk",
            default=None,
            help="Optional Device UUID to verify DeviceUIViewSet.get_object() for edit view.",
        )

    def handle(self, *args, **options):
        """Execute diagnostics and print a human-readable report."""
        device_pk = options.get("device_pk")
        self.stdout.write("Nautobot Function Codes diagnostics")
        self.stdout.write(f"debug_logging={is_debug_logging_enabled()}")
        self.stdout.write("")

        results = collect_device_integration_diagnostics(device_pk=device_pk)
        has_errors = False
        for result in results:
            prefix = result.status.upper()
            self.stdout.write(f"[{prefix}] {result.check}: {result.message}")
            if result.status == "error":
                has_errors = True

        self.stdout.write("")
        if has_errors:
            self.stderr.write(self.style.ERROR("Diagnostics found errors. See messages above."))
            self.stderr.write(
                "Tip: enable verbose logs with PLUGINS_CONFIG['nautobot_function_codes']['debug_logging'] = True"
            )
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS("All diagnostics passed."))
