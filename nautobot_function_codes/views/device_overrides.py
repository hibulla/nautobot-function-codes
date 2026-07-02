"""Device UI integration for Function Code assignment."""

from django.db import transaction
from nautobot.dcim.views import DeviceUIViewSet

from nautobot_function_codes.forms.device import DeviceBulkEditFormWithFunctionCode, DeviceFormWithFunctionCode
from nautobot_function_codes.utils import set_device_function_code


def _get_queryset_with_function_code(self):
    """Prefetch Function Code assignment data for list, detail, and edit views."""
    queryset = self._nautobot_function_codes_original_get_queryset()
    if self.action in ("retrieve", "list", "update"):
        queryset = queryset.select_related("function_code_assignment__function_code")
    return queryset


def _process_create_or_update_form_with_function_code(self, form):
    """Save Device changes and persist the Function Code assignment."""
    function_code = form.cleaned_data.get("function_code")
    self._nautobot_function_codes_original_process_create_or_update_form(form)
    set_device_function_code(form.instance, function_code)


def _process_bulk_update_form_with_function_code(self, form):
    """Bulk update Devices and optionally update Function Code assignments."""
    function_code = form.cleaned_data.get("function_code")
    with transaction.atomic():
        self._nautobot_function_codes_original_process_bulk_update_form(form)
        if "function_code" in form.changed_data:
            for device in form.cleaned_data["pk"]:
                set_device_function_code(device, function_code)


def integrate_device_views():
    """Patch the core Device viewset instead of replacing its URL callbacks.

    Replacing `dcim:device_edit` via `override_views` drops router initkwargs such as
    `detail=True`, which prevents Nautobot from loading the Device instance on edit.
    """
    if getattr(DeviceUIViewSet, "_nautobot_function_codes_integrated", False):
        return

    DeviceUIViewSet._nautobot_function_codes_original_get_queryset = DeviceUIViewSet.get_queryset
    DeviceUIViewSet._nautobot_function_codes_original_process_create_or_update_form = (
        DeviceUIViewSet._process_create_or_update_form
    )
    DeviceUIViewSet._nautobot_function_codes_original_process_bulk_update_form = (
        DeviceUIViewSet._process_bulk_update_form
    )

    DeviceUIViewSet.form_class = DeviceFormWithFunctionCode
    DeviceUIViewSet.bulk_update_form_class = DeviceBulkEditFormWithFunctionCode
    DeviceUIViewSet.get_queryset = _get_queryset_with_function_code
    DeviceUIViewSet._process_create_or_update_form = _process_create_or_update_form_with_function_code
    DeviceUIViewSet._process_bulk_update_form = _process_bulk_update_form_with_function_code
    DeviceUIViewSet._nautobot_function_codes_integrated = True
