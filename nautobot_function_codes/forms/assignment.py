"""Forms for managing Device Function Code assignments."""

from django import forms
from nautobot.apps.forms import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
)
from nautobot.dcim.models import Device

from nautobot_function_codes import models


class DeviceFunctionCodeAssignmentForm(NautobotModelForm):
    """Create or edit a single Device Function Code assignment."""

    class Meta:
        """Meta attributes."""

        model = models.DeviceFunctionCodeAssignment
        fields = ["device", "function_code"]


class DeviceFunctionCodeAssignmentBulkEditForm(NautobotBulkEditForm):
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
    field_order = ["device", "function_code"]

    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    function_code = DynamicModelChoiceField(
        queryset=models.FunctionCode.objects.all(),
        required=False,
        label="Function Code",
    )


class FunctionCodeAssignDevicesForm(forms.Form):
    """Assign one or more devices to a Function Code."""

    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label="Devices",
        help_text="Selected devices will be assigned to this Function Code. Existing assignments are updated.",
    )
