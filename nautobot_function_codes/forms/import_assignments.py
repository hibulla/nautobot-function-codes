"""Forms for CSV import of device assignments."""

from django import forms
from nautobot.apps.forms import BootstrapMixin


class ImportAssignmentsForm(BootstrapMixin, forms.Form):
    """Upload a CSV file to import device Function Code assignments."""

    csv_file = forms.FileField(
        required=True,
        label="CSV File",
        help_text="Required columns: device, function_code",
    )
    dry_run = forms.BooleanField(
        required=False,
        initial=False,
        label="Dry run",
        help_text="Validate the file without saving changes.",
    )
