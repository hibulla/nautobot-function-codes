"""Generate test data for the Nautobot Function Codes app."""

from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS

from nautobot_function_codes.models import FunctionCode


class Command(BaseCommand):
    """Populate the database with various data as a baseline for testing (automated or manual)."""

    help = __doc__

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help='The database to generate the test data in. Defaults to the "default" database.',
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Flush any existing Nautobot Function Codes test data from the database before generating new data.",
        )

    def _generate_static_data(self, db):
        """Generate static FunctionCode records for manual testing."""
        defaults = [
            {"name": "WAN", "slug": "wan", "description": "Wide area network device"},
            {"name": "ACC", "slug": "acc", "description": "Access layer device"},
            {"name": "COR", "slug": "cor", "description": "Core layer device"},
            {"name": "DIS", "slug": "dis", "description": "Distribution layer device"},
        ]
        for entry in defaults:
            FunctionCode.objects.using(db).get_or_create(slug=entry["slug"], defaults=entry)

    def handle(self, *args, **options):
        """Entry point to the management command."""
        if options["flush"]:
            self.stdout.write("Flushing existing Nautobot Function Codes test data...")
            FunctionCode.objects.using(options["database"]).all().delete()

        self._generate_static_data(db=options["database"])

        self.stdout.write(self.style.SUCCESS(f"Database {options['database']} populated with app data successfully!"))
