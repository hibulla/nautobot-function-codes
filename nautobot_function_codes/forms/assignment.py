"""Forms for managing Device Function Code assignments."""

from django import forms
from nautobot.apps.forms import (
    BootstrapMixin,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    NautobotFilterForm,
)
from nautobot.core.forms import BulkEditForm
from nautobot.dcim.models import Device

from nautobot_function_codes import models

_DEVICES_FIELD_HELP_TEXT = (
    "Select multiple devices: pick one from the dropdown, then search and add more "
    "(each appears as a tag), or use the search button to filter and add devices."
)


class DeviceFunctionCodeAssignmentForm(forms.ModelForm):
    """Edit an existing Device Function Code assignment."""

    function_code = DynamicModelChoiceField(
        queryset=models.FunctionCode.objects.filter(is_active=True),
        required=False,
        label="Function Code",
    )

    class Meta:
        """Meta attributes."""

        model = models.DeviceFunctionCodeAssignment
        fields = ["device", "function_code"]


class DeviceFunctionCodeAssignmentBulkEditForm(BootstrapMixin, BulkEditForm):
    """Bulk update Function Code assignments."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.DeviceFunctionCodeAssignment.objects.all(),
        widget=forms.MultipleHiddenInput,
    )
    function_code = DynamicModelChoiceField(
        queryset=models.FunctionCode.objects.filter(is_active=True),
        required=False,
        label="Function Code",
    )

    class Meta:
        """Meta attributes."""

        nullable_fields = ["function_code"]


class DeviceFunctionCodeAssignmentFilterForm(NautobotFilterForm):
    """Filter form for assignment list views."""

    model = models.DeviceFunctionCodeAssignment
    field_order = ["device", "function_code", "function_code_is_active"]

    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    function_code = DynamicModelChoiceField(
        queryset=models.FunctionCode.objects.all(),
        required=False,
        label="Function Code",
    )
    function_code_is_active = forms.NullBooleanField(required=False, label="Function Code Active")


class FunctionCodeAssignDevicesForm(forms.Form):
    """Assign one or more devices to a Function Code selected on the previous screen."""

    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label="Devices",
        embedded_search=True,
        help_text=_DEVICES_FIELD_HELP_TEXT,
    )


class BulkAssignDevicesForm(forms.Form):
    """Assign one or more devices to a chosen Function Code."""

    function_code = DynamicModelChoiceField(
        queryset=models.FunctionCode.objects.filter(is_active=True),
        required=True,
        label="Function Code",
    )
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label="Devices",
        embedded_search=True,
        help_text=_DEVICES_FIELD_HELP_TEXT,
    )

    def __init__(self, *args, instance=None, **kwargs):
        """Accept Nautobot create-view kwargs such as ``instance`` for non-model forms."""
        super().__init__(*args, **kwargs)


class ClearDeviceFunctionCodeAssignmentsForm(forms.Form):
    """Clear Function Code assignments from one or more devices."""

    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.filter(function_code_assignment__function_code__isnull=False),
        required=True,
        label="Devices",
        embedded_search=True,
        help_text="Select devices whose Function Code assignment should be cleared.",
    )
