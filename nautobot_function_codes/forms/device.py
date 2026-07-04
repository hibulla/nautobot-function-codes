"""Forms for Device Function Code integration."""

from django import forms
from nautobot.apps.forms import DynamicModelChoiceField

from nautobot_function_codes import models


class DeviceFunctionCodePanelForm(forms.Form):
    """Update the Function Code assigned to a device from the Device detail panel."""

    function_code = DynamicModelChoiceField(
        queryset=models.FunctionCode.objects.filter(is_active=True),
        required=False,
        label="Function Code",
        help_text="Leave empty to clear the assignment.",
    )
