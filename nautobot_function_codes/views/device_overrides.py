"""Device UI integration for Function Code assignment."""

# Patching Nautobot viewset hooks requires assigning to leading-underscore methods.
# pylint: disable=protected-access

from django.db import transaction
from nautobot.dcim.views import DeviceUIViewSet
from nautobot.extras.plugins import register_override_views

from nautobot_function_codes.debug_utils import LOGGER, debug_log
from nautobot_function_codes.forms.device import DeviceBulkEditFormWithFunctionCode, DeviceFormWithFunctionCode
from nautobot_function_codes.utils import set_device_function_code


class _DeviceViewIntegrationState:
    """Hold original Device viewset hooks while integrating Function Code support."""

    integrated = False
    original_get_queryset = None
    original_process_create_or_update_form = None
    original_process_bulk_update_form = None
    original_update = None


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
    debug_log(
        "Processing Device create/update form: device_pk=%s function_code=%s",
        getattr(form.instance, "pk", None),
        getattr(function_code, "pk", function_code),
    )
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


def _update_with_function_code(self, request, *args, **kwargs):
    """Ensure Nautobot loads the Device instance when rendering the edit form."""
    debug_log(
        "Device update request: method=%s action=%s detail=%s kwargs=%s",
        request.method,
        getattr(self, "action", None),
        getattr(self, "detail", None),
        kwargs,
    )
    self.detail = True
    debug_log("Device update: forced detail=True before calling core update()")
    try:
        return _STATE.original_update(self, request, *args, **kwargs)
    except Exception:
        LOGGER.exception(
            "Device update failed after Function Code integration (method=%s kwargs=%s detail=%s)",
            request.method,
            kwargs,
            self.detail,
        )
        raise


def is_device_view_integration_complete():
    """Return True when Device UI integration has been applied."""
    return _STATE.integrated


def is_device_update_wrapped():
    """Return True when DeviceUIViewSet.update uses the Function Code wrapper."""
    return DeviceUIViewSet.update is _update_with_function_code


def integrate_device_views():
    """Extend the core Device UI with Function Code support.

    We patch `DeviceUIViewSet` for form/save behavior and re-register Device UI routes
    with the router initkwargs Nautobot expects (especially `detail=True` for edit).
    """
    if _STATE.integrated:
        return

    _STATE.original_get_queryset = DeviceUIViewSet.get_queryset
    _STATE.original_process_create_or_update_form = DeviceUIViewSet._process_create_or_update_form
    _STATE.original_process_bulk_update_form = DeviceUIViewSet._process_bulk_update_form
    _STATE.original_update = DeviceUIViewSet.update

    DeviceUIViewSet.form_class = DeviceFormWithFunctionCode
    DeviceUIViewSet.bulk_update_form_class = DeviceBulkEditFormWithFunctionCode
    DeviceUIViewSet.get_queryset = _get_queryset_with_function_code
    DeviceUIViewSet._process_create_or_update_form = _process_create_or_update_form_with_function_code
    DeviceUIViewSet._process_bulk_update_form = _process_bulk_update_form_with_function_code
    DeviceUIViewSet.update = _update_with_function_code

    # Replace any prior plugin URL overrides that omitted router initkwargs like detail=True.
    override_views = {
        "dcim:device_edit": DeviceUIViewSet.as_view(
            {"get": "update", "post": "update"},
            detail=True,
            basename="device",
            suffix="Edit",
        ),
        "dcim:device_add": DeviceUIViewSet.as_view(
            {"get": "create", "post": "create"},
            detail=False,
            basename="device",
            suffix="Add",
        ),
        "dcim:device_bulk_edit": DeviceUIViewSet.as_view(
            {"get": "bulk_update", "post": "bulk_update"},
            detail=False,
            basename="device",
            suffix="Bulk Edit",
        ),
    }
    register_override_views(override_views, "nautobot_function_codes")

    _STATE.integrated = True
    LOGGER.info(
        "Device UI integration complete (form_class=%s, overrides=%s)",
        DeviceFormWithFunctionCode.__name__,
        sorted(override_views.keys()),
    )
    for qualified_view_name, view in override_views.items():
        debug_log(
            "Registered override %s: view_class=%s initkwargs=%s",
            qualified_view_name,
            getattr(view, "cls", type(view)).__name__,
            getattr(view, "initkwargs", {}),
        )
