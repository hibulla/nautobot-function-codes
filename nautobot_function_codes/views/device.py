"""Views for updating Function Code from Device detail."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from nautobot.core.forms import restrict_form_fields
from nautobot.core.views.mixins import ContentTypePermissionRequiredMixin
from nautobot.dcim.models import Device

from nautobot_function_codes.forms.device import DeviceFunctionCodePanelForm
from nautobot_function_codes.utils import get_device_function_code, set_device_function_code


class DeviceSetFunctionCodeView(ContentTypePermissionRequiredMixin, View):
    """Update or clear the Function Code assigned to a device."""

    queryset = Device.objects.all()

    def get_required_permission(self):
        """Require permission to change Function Code assignments."""
        return "nautobot_function_codes.change_devicefunctioncodeassignment"

    def post(self, request, pk):
        """Apply the submitted Function Code assignment."""
        device = get_object_or_404(self.queryset, pk=pk)
        form = DeviceFunctionCodePanelForm(request.POST)
        restrict_form_fields(form, request.user)

        if not form.is_valid():
            messages.error(request, "Unable to update Function Code assignment.")
            return redirect(device.get_absolute_url())

        function_code = form.cleaned_data["function_code"]
        previous_function_code = get_device_function_code(device)
        try:
            set_device_function_code(device, function_code)
        except ValidationError as exc:
            message = exc.message_dict.get("function_code", exc.messages)
            if isinstance(message, list):
                message = message[0]
            messages.error(request, message)
            return redirect(device.get_absolute_url())

        if function_code is None:
            if previous_function_code is None:
                messages.info(request, f"No Function Code assignment to change for {device.name}.")
            else:
                messages.success(request, f"Cleared Function Code assignment for {device.name}.")
        else:
            messages.success(request, f"Assigned {function_code.name} to {device.name}.")

        return redirect(device.get_absolute_url())
