"""Runtime diagnostics for nautobot_function_codes."""

from dataclasses import dataclass

from django.urls import get_resolver
from django.urls.exceptions import NoReverseMatch, Resolver404
from django.urls.resolvers import URLPattern
from nautobot.dcim.views import DeviceUIViewSet

from nautobot_function_codes.forms.device import DeviceBulkEditFormWithFunctionCode, DeviceFormWithFunctionCode
from nautobot_function_codes.views.device_overrides import (
    is_device_update_wrapped,
    is_device_view_integration_complete,
)

DEVICE_URL_OVERRIDES = {
    "dcim:device_edit": True,
    "dcim:device_add": False,
    "dcim:device_bulk_edit": False,
}


@dataclass(frozen=True)
class DiagnosticResult:
    """Single diagnostic check outcome."""

    status: str
    check: str
    message: str


def _resolve_url_callback(qualified_view_name):
    """Return the URL callback registered for a fully qualified view name."""
    qualified_app_name, view_name = qualified_view_name.rsplit(":", 1)
    app_resolver = get_resolver()
    for app_name in qualified_app_name.split(":"):
        app_resolver_tuple = app_resolver.namespace_dict.get(app_name)
        if app_resolver_tuple is None:
            raise Resolver404(f"Namespace '{app_name}' not found for {qualified_view_name}")
        app_resolver = app_resolver_tuple[1]

    for pattern in app_resolver.url_patterns:
        if isinstance(pattern, URLPattern) and pattern.name == view_name:
            return pattern.callback

    raise Resolver404(f"View '{view_name}' not found under '{qualified_app_name}'")


def _view_initkwargs(callback):
    """Return router initkwargs from a DRF ViewSet.as_view() callback."""
    return getattr(callback, "initkwargs", None)


def _view_class_name(callback):
    """Return the view class name from a DRF ViewSet.as_view() callback."""
    view_class = getattr(callback, "cls", None) or getattr(callback, "view_class", None)
    if view_class is None:
        return repr(callback)
    return view_class.__name__


def _integration_state_result():
    """Return a diagnostic result for Device UI integration state."""
    integrated = is_device_view_integration_complete()
    return DiagnosticResult(
        status="ok" if integrated else "error",
        check="integration_state",
        message=f"Device integration flag integrated={integrated}",
    )


def _device_form_class_result():
    """Return a diagnostic result for the Device edit form class."""
    form_ok = DeviceUIViewSet.form_class is DeviceFormWithFunctionCode
    form_class_name = getattr(DeviceUIViewSet.form_class, "__name__", DeviceUIViewSet.form_class)
    return DiagnosticResult(
        status="ok" if form_ok else "error",
        check="device_form_class",
        message=f"DeviceUIViewSet.form_class={form_class_name} (expected {DeviceFormWithFunctionCode.__name__})",
    )


def _device_bulk_form_class_result():
    """Return a diagnostic result for the Device bulk edit form class."""
    bulk_form_ok = DeviceUIViewSet.bulk_update_form_class is DeviceBulkEditFormWithFunctionCode
    bulk_form_class_name = getattr(
        DeviceUIViewSet.bulk_update_form_class,
        "__name__",
        DeviceUIViewSet.bulk_update_form_class,
    )
    return DiagnosticResult(
        status="ok" if bulk_form_ok else "error",
        check="device_bulk_form_class",
        message=(
            f"DeviceUIViewSet.bulk_update_form_class={bulk_form_class_name} "
            f"(expected {DeviceBulkEditFormWithFunctionCode.__name__})"
        ),
    )


def _device_update_wrapper_result():
    """Return a diagnostic result for the Device update view wrapper."""
    update_ok = is_device_update_wrapped()
    return DiagnosticResult(
        status="ok" if update_ok else "warning",
        check="device_update_wrapper",
        message=(
            "DeviceUIViewSet.update is patched"
            if update_ok
            else "DeviceUIViewSet.update is not the Function Code wrapper"
        ),
    )


def _url_override_result(qualified_view_name, expected_detail):
    """Return a diagnostic result for a Device URL override initkwargs check."""
    check = f"url_{qualified_view_name.replace(':', '_')}"
    try:
        callback = _resolve_url_callback(qualified_view_name)
        initkwargs = _view_initkwargs(callback) or {}
        detail = initkwargs.get("detail")
        detail_ok = detail is expected_detail
        return DiagnosticResult(
            status="ok" if detail_ok else "error",
            check=check,
            message=(
                f"{qualified_view_name}: detail={detail} (expected {expected_detail}), "
                f"callback={_view_class_name(callback)}, initkwargs={initkwargs}"
            ),
        )
    except (Resolver404, NoReverseMatch, ValueError) as exc:
        return DiagnosticResult(
            status="error",
            check=check,
            message=f"Could not inspect {qualified_view_name}: {exc}",
        )


def _device_get_object_result(device_pk):
    """Return a diagnostic result for DeviceUIViewSet.get_object() on edit."""
    try:
        from django.contrib.auth import get_user_model
        from django.test import RequestFactory
        from nautobot.dcim.models import Device

        device = Device.objects.get(pk=device_pk)
        user_model = get_user_model()
        user = user_model.objects.filter(is_superuser=True).first()
        if user is None:
            return DiagnosticResult(
                status="warning",
                check="device_get_object",
                message="Skipped get_object() check: no superuser in database",
            )

        request = RequestFactory().get(f"/dcim/devices/{device.pk}/edit/")
        request.user = user

        viewset = DeviceUIViewSet()
        viewset.setup(request, pk=str(device.pk))
        viewset.action = "update"
        viewset.detail = True
        instance = viewset.get_object()
        return DiagnosticResult(
            status="ok" if instance is not None else "error",
            check="device_get_object",
            message=(
                f"get_object() returned {type(instance).__name__ if instance else None} "
                f"for pk={device_pk}, present_in_database={getattr(instance, 'present_in_database', None)}"
            ),
        )
    except Exception as exc:  # pylint: disable=broad-except
        return DiagnosticResult(
            status="error",
            check="device_get_object",
            message=f"get_object() failed for pk={device_pk}: {type(exc).__name__}: {exc}",
        )


def collect_device_integration_diagnostics(device_pk=None):
    """Collect diagnostics for Device UI integration.

    Returns a list of DiagnosticResult entries suitable for logging or CLI output.
    """
    results = [
        _integration_state_result(),
        _device_form_class_result(),
        _device_bulk_form_class_result(),
        _device_update_wrapper_result(),
    ]
    results.extend(
        _url_override_result(qualified_view_name, expected_detail)
        for qualified_view_name, expected_detail in DEVICE_URL_OVERRIDES.items()
    )
    if device_pk:
        results.append(_device_get_object_result(device_pk))
    return results
