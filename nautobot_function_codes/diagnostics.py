"""Runtime diagnostics for nautobot_function_codes."""

from dataclasses import dataclass

from django.urls import get_resolver
from django.urls.exceptions import NoReverseMatch, Resolver404
from django.urls.resolvers import URLPattern

from nautobot.dcim.views import DeviceUIViewSet

from nautobot_function_codes.forms.device import DeviceBulkEditFormWithFunctionCode, DeviceFormWithFunctionCode
from nautobot_function_codes.views import device_overrides


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


def collect_device_integration_diagnostics(device_pk=None):
    """Collect diagnostics for Device UI integration.

    Returns a list of DiagnosticResult entries suitable for logging or CLI output.
    """
    results = []

    state = device_overrides._STATE  # pylint: disable=protected-access
    results.append(
        DiagnosticResult(
            status="ok" if state.integrated else "error",
            check="integration_state",
            message=f"Device integration flag integrated={state.integrated}",
        )
    )

    form_ok = DeviceUIViewSet.form_class is DeviceFormWithFunctionCode
    results.append(
        DiagnosticResult(
            status="ok" if form_ok else "error",
            check="device_form_class",
            message=(
                f"DeviceUIViewSet.form_class={getattr(DeviceUIViewSet.form_class, '__name__', DeviceUIViewSet.form_class)} "
                f"(expected {DeviceFormWithFunctionCode.__name__})"
            ),
        )
    )

    bulk_form_ok = DeviceUIViewSet.bulk_update_form_class is DeviceBulkEditFormWithFunctionCode
    results.append(
        DiagnosticResult(
            status="ok" if bulk_form_ok else "error",
            check="device_bulk_form_class",
            message=(
                "DeviceUIViewSet.bulk_update_form_class="
                f"{getattr(DeviceUIViewSet.bulk_update_form_class, '__name__', DeviceUIViewSet.bulk_update_form_class)} "
                f"(expected {DeviceBulkEditFormWithFunctionCode.__name__})"
            ),
        )
    )

    update_ok = DeviceUIViewSet.update is device_overrides._update_with_function_code
    results.append(
        DiagnosticResult(
            status="ok" if update_ok else "warning",
            check="device_update_wrapper",
            message=(
                "DeviceUIViewSet.update is patched"
                if update_ok
                else "DeviceUIViewSet.update is not the Function Code wrapper"
            ),
        )
    )

    expected_detail = {
        "dcim:device_edit": True,
        "dcim:device_add": False,
        "dcim:device_bulk_edit": False,
    }
    for qualified_view_name, expected in expected_detail.items():
        try:
            callback = _resolve_url_callback(qualified_view_name)
            initkwargs = _view_initkwargs(callback) or {}
            detail = initkwargs.get("detail")
            detail_ok = detail is expected
            results.append(
                DiagnosticResult(
                    status="ok" if detail_ok else "error",
                    check=f"url_{qualified_view_name.replace(':', '_')}",
                    message=(
                        f"{qualified_view_name}: detail={detail} (expected {expected}), "
                        f"callback={_view_class_name(callback)}, initkwargs={initkwargs}"
                    ),
                )
            )
        except (Resolver404, NoReverseMatch, ValueError) as exc:
            results.append(
                DiagnosticResult(
                    status="error",
                    check=f"url_{qualified_view_name.replace(':', '_')}",
                    message=f"Could not inspect {qualified_view_name}: {exc}",
                )
            )

    if device_pk:
        try:
            from nautobot.dcim.models import Device

            device = Device.objects.get(pk=device_pk)
            viewset = DeviceUIViewSet()
            viewset.action = "update"
            viewset.kwargs = {"pk": str(device.pk)}
            viewset.detail = True
            instance = viewset.get_object()
            results.append(
                DiagnosticResult(
                    status="ok" if instance is not None else "error",
                    check="device_get_object",
                    message=(
                        f"get_object() returned {type(instance).__name__ if instance else None} "
                        f"for pk={device_pk}, present_in_database="
                        f"{getattr(instance, 'present_in_database', None)}"
                    ),
                )
            )
        except Exception as exc:  # pylint: disable=broad-except
            results.append(
                DiagnosticResult(
                    status="error",
                    check="device_get_object",
                    message=f"get_object() failed for pk={device_pk}: {type(exc).__name__}: {exc}",
                )
            )

    return results
