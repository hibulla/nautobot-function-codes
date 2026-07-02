"""Device UI integration for Function Code assignment."""

# Patching Nautobot viewset hooks requires assigning to leading-underscore methods.
# pylint: disable=protected-access

from django.db import transaction
from nautobot.dcim.views import DeviceUIViewSet

from nautobot_function_codes.forms.device import DeviceBulkEditFormWithFunctionCode, DeviceFormWithFunctionCode
from nautobot_function_codes.utils import set_device_function_code


class _DeviceViewIntegrationState:
    """Hold original Device viewset hooks while integrating Function Code support."""

    integrated = False
    original_get_queryset = None
    original_process_create_or_update_form = None
    original_process_bulk_update_form = None


_STATE = _DeviceViewIntegrationState()


def _get_queryset_with_function_code(self):
    """Prefetch Function Code assignment data for list, detail, and edit views."""
    queryset = _STATE.original_get_queryset(self)
    if self.action in ("retrieve", "list", "update"):
        queryset = queryset.select_related("function_code_assignment__function_code")
    return queryset


def _process_create_or_update_form_with_function_code(self, form):
    """Save Device changes and persist the Function Code assignment."""
    function_code = form.cleaned_data.get("function_code")
    _STATE.original_process_create_or_update_form(self, form)
    set_device_function_code(form.instance, function_code)


def _process_bulk_update_form_with_function_code(self, form):
    """Bulk update Devices and optionally update Function Code assignments."""
    function_code = form.cleaned_data.get("function_code")
    with transaction.atomic():
        _STATE.original_process_bulk_update_form(self, form)
        if "function_code" in form.changed_data:
            for device in form.cleaned_data["pk"]:
                set_device_function_code(device, function_code)


def integrate_device_views():
    """Patch the core Device viewset instead of replacing its URL callbacks.

    Replacing `dcim:device_edit` via `override_views` drops router initkwargs such as
    `detail=True`, which prevents Nautobot from loading the Device instance on edit.
    """
    if _STATE.integrated:
        return

    _STATE.original_get_queryset = DeviceUIViewSet.get_queryset
    _STATE.original_process_create_or_update_form = DeviceUIViewSet._process_create_or_update_form
    _STATE.original_process_bulk_update_form = DeviceUIViewSet._process_bulk_update_form

    DeviceUIViewSet.form_class = DeviceFormWithFunctionCode
    DeviceUIViewSet.bulk_update_form_class = DeviceBulkEditFormWithFunctionCode
    DeviceUIViewSet.get_queryset = _get_queryset_with_function_code
    DeviceUIViewSet._process_create_or_update_form = _process_create_or_update_form_with_function_code
    DeviceUIViewSet._process_bulk_update_form = _process_bulk_update_form_with_function_code
    _STATE.integrated = True
