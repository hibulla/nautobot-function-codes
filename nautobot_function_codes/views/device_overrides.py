"""Device UI integration for Function Code assignment."""

# Patching Nautobot viewset hooks requires assigning to leading-underscore methods.
# pylint: disable=protected-access

from django.db import transaction
from nautobot.dcim.views import DeviceUIViewSet

from nautobot_function_codes.debug_utils import LOGGER, debug_log
from nautobot_function_codes.forms.device import DeviceBulkEditFormWithFunctionCode, DeviceFormWithFunctionCode
from nautobot_function_codes.utils import set_device_function_code


class _DeviceViewIntegrationState:
    """Hold original Device viewset hooks while integrating Function Code support."""

    integrated = False
    device_create_template = "nautobot_function_codes/dcim/device_create.html"
    original_get_queryset = None
    original_get_template_name = None
    original_initialize_request = None
    original_process_create_or_update_form = None
    original_process_bulk_update_form = None


_STATE = _DeviceViewIntegrationState()


def _get_queryset_with_function_code(self):
    """Prefetch Function Code assignment data for list, detail, and edit views."""
    queryset = _STATE.original_get_queryset(self)
    if self.action in ("retrieve", "list", "update"):
        queryset = queryset.select_related("function_code_assignment__function_code")
    return queryset


def _get_template_name_with_function_code(self):
    """Use a Device create/edit template that renders the Function Code field.

    Core ``dcim/device_create.html`` lists each field explicitly, so extra form
    fields from ``DeviceFormWithFunctionCode`` are omitted unless we extend it.
    """
    if self.action in ("create", "update"):
        return _STATE.device_create_template
    return _STATE.original_get_template_name(self)


def _initialize_request_with_function_code(self, request, *args, **kwargs):
    """Ensure edit requests load the Device instance in NautobotHTMLRenderer.

    Nautobot only calls get_object() when view.detail is True. Some third-party
    plugins re-register dcim:device_edit without detail=True; force it here so
    the core Device edit form (now extended with Function Code) keeps working.
    """
    request = _STATE.original_initialize_request(self, request, *args, **kwargs)
    if self.action == "update":
        self.detail = True
        debug_log(
            "Device viewset initialize_request: forced detail=True for action=update kwargs=%s",
            kwargs,
        )
    return request


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


def _patch_device_viewset():
    """Patch DeviceUIViewSet hooks used by the Function Code integration."""
    _STATE.original_get_queryset = DeviceUIViewSet.get_queryset
    _STATE.original_get_template_name = DeviceUIViewSet.get_template_name
    _STATE.original_initialize_request = DeviceUIViewSet.initialize_request
    _STATE.original_process_create_or_update_form = DeviceUIViewSet._process_create_or_update_form
    _STATE.original_process_bulk_update_form = DeviceUIViewSet._process_bulk_update_form

    DeviceUIViewSet.form_class = DeviceFormWithFunctionCode
    DeviceUIViewSet.bulk_update_form_class = DeviceBulkEditFormWithFunctionCode
    DeviceUIViewSet.get_queryset = _get_queryset_with_function_code
    DeviceUIViewSet.get_template_name = _get_template_name_with_function_code
    DeviceUIViewSet.initialize_request = _initialize_request_with_function_code
    DeviceUIViewSet._process_create_or_update_form = _process_create_or_update_form_with_function_code
    DeviceUIViewSet._process_bulk_update_form = _process_bulk_update_form_with_function_code


def is_device_view_integration_complete():
    """Return True when Device UI integration has been applied."""
    return _STATE.integrated


def is_device_initialize_request_wrapped():
    """Return True when DeviceUIViewSet.initialize_request uses the Function Code wrapper."""
    return DeviceUIViewSet.initialize_request is _initialize_request_with_function_code


def is_device_get_template_name_wrapped():
    """Return True when DeviceUIViewSet.get_template_name uses the Function Code wrapper."""
    return DeviceUIViewSet.get_template_name is _get_template_name_with_function_code


def get_device_create_template_name():
    """Return the plugin template used for Device create/edit views."""
    return _STATE.device_create_template


def integrate_device_views():
    """Extend the core Device UI with Function Code support.

    This patches the shared DeviceUIViewSet class only. It deliberately does
    not register override_views for dcim:device_* routes, so we do not compete
    with other plugins for URL ownership or risk breaking detail=True routing.
    """
    if _STATE.integrated:
        return

    _patch_device_viewset()
    _STATE.integrated = True
    LOGGER.info(
        "Device UI integration complete (form_class=%s, patches=DeviceUIViewSet only, no URL overrides)",
        DeviceFormWithFunctionCode.__name__,
    )
