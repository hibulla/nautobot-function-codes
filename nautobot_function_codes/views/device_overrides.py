"""Device view overrides for Function Code integration."""

from django.db import transaction
from nautobot.dcim.views import DeviceUIViewSet

from nautobot_function_codes.forms.device import DeviceBulkEditFormWithFunctionCode, DeviceFormWithFunctionCode
from nautobot_function_codes.utils import set_device_function_code


class DeviceUIViewSetWithFunctionCode(DeviceUIViewSet):
    """DeviceUIViewSet extended with Function Code assignment support."""

    form_class = DeviceFormWithFunctionCode
    bulk_update_form_class = DeviceBulkEditFormWithFunctionCode

    def get_queryset(self):
        """Prefetch Function Code assignment data for list and detail views."""
        queryset = super().get_queryset()
        if self.action in ("retrieve", "list"):
            queryset = queryset.select_related("function_code_assignment__function_code")
        return queryset

    def _process_create_or_update_form(self, form):
        function_code = form.cleaned_data.get("function_code")
        super()._process_create_or_update_form(form)
        set_device_function_code(form.instance, function_code)

    def _process_bulk_update_form(self, form):
        function_code = form.cleaned_data.get("function_code")
        with transaction.atomic():
            super()._process_bulk_update_form(form)
            if "function_code" in form.changed_data:
                for device in form.cleaned_data["pk"]:
                    set_device_function_code(device, function_code)


override_views = {
    "dcim:device_add": DeviceUIViewSetWithFunctionCode.as_view({"get": "create", "post": "create"}),
    "dcim:device_edit": DeviceUIViewSetWithFunctionCode.as_view({"get": "update", "post": "update"}),
    "dcim:device_bulk_edit": DeviceUIViewSetWithFunctionCode.as_view({"get": "bulk_update", "post": "bulk_update"}),
}
