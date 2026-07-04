"""Runtime diagnostics for nautobot_function_codes."""

from dataclasses import dataclass
from importlib import metadata

from django.urls import reverse

from nautobot_function_codes import models


@dataclass(frozen=True)
class DiagnosticResult:
    """Single diagnostic check outcome."""

    status: str
    check: str
    message: str


def _plugin_models_result():
    """Return a diagnostic result for core plugin models."""
    function_code_count = models.FunctionCode.objects.count()
    assignment_count = models.DeviceFunctionCodeAssignment.objects.count()
    return DiagnosticResult(
        status="ok",
        check="plugin_models",
        message=(
            f"FunctionCode records={function_code_count}, " f"DeviceFunctionCodeAssignment records={assignment_count}"
        ),
    )


def _assignment_ui_routes_result():
    """Return a diagnostic result for assignment UI route registration."""
    try:
        list_url = reverse("plugins:nautobot_function_codes:devicefunctioncodeassignment_list")
        assign_url = reverse(
            "plugins:nautobot_function_codes:functioncode_assign_devices",
            kwargs={"pk": "00000000-0000-0000-0000-000000000001"},
        )
        return DiagnosticResult(
            status="ok",
            check="assignment_ui_routes",
            message=f"Assignment UI routes registered: list={list_url}, assign_devices={assign_url}",
        )
    except Exception as exc:  # pylint: disable=broad-except
        return DiagnosticResult(
            status="error",
            check="assignment_ui_routes",
            message=f"Assignment UI routes are not registered: {type(exc).__name__}: {exc}",
        )


def _assignment_list_http_result():
    """Return a diagnostic result for the assignment list HTTP view."""
    try:
        from django.contrib.auth import get_user_model
        from django.test import Client

        user_model = get_user_model()
        user = user_model.objects.filter(is_superuser=True).first()
        if user is None:
            return DiagnosticResult(
                status="warning",
                check="assignment_list_http",
                message="Skipped assignment list HTTP check: no superuser in database",
            )

        client = Client()
        client.force_login(user)
        url = reverse("plugins:nautobot_function_codes:devicefunctioncodeassignment_list")
        response = client.get(url)
        return DiagnosticResult(
            status="ok" if response.status_code == 200 else "error",
            check="assignment_list_http",
            message=f"GET {url} returned HTTP {response.status_code}",
        )
    except Exception as exc:  # pylint: disable=broad-except
        return DiagnosticResult(
            status="error",
            check="assignment_list_http",
            message=f"Assignment list HTTP check failed: {type(exc).__name__}: {exc}",
        )


def _plugin_version_result():
    """Return a diagnostic result for the installed plugin package version."""
    try:
        version = metadata.version("nautobot-function-codes")
        return DiagnosticResult(
            status="ok",
            check="plugin_version",
            message=f"Installed nautobot-function-codes version: {version}",
        )
    except metadata.PackageNotFoundError:
        return DiagnosticResult(
            status="warning",
            check="plugin_version",
            message="Installed nautobot-function-codes package version is unknown (editable or non-standard install)",
        )


def _extended_ui_routes_result():
    """Return a diagnostic result for v0.2 UI route registration."""
    try:
        coverage_url = reverse("plugins:nautobot_function_codes:coverage_dashboard")
        import_url = reverse("plugins:nautobot_function_codes:import_assignments")
        device_url = reverse(
            "plugins:nautobot_function_codes:device_set_function_code",
            kwargs={"pk": "00000000-0000-0000-0000-000000000001"},
        )
        return DiagnosticResult(
            status="ok",
            check="extended_ui_routes",
            message=(
                f"Extended UI routes registered: coverage={coverage_url}, "
                f"import_assignments={import_url}, device_set_function_code={device_url}"
            ),
        )
    except Exception as exc:  # pylint: disable=broad-except
        return DiagnosticResult(
            status="error",
            check="extended_ui_routes",
            message=f"Extended UI routes are not registered: {type(exc).__name__}: {exc}",
        )


def _jobs_module_result():
    """Return a diagnostic result for plugin job registration."""
    try:
        from nautobot_function_codes.jobs import jobs as jobs_module

        job_count = len(jobs_module.jobs)
        return DiagnosticResult(
            status="ok",
            check="plugin_jobs",
            message=f"Plugin jobs module loaded with {job_count} job class(es)",
        )
    except Exception as exc:  # pylint: disable=broad-except
        return DiagnosticResult(
            status="error",
            check="plugin_jobs",
            message=f"Plugin jobs module failed to load: {type(exc).__name__}: {exc}",
        )


def collect_plugin_diagnostics():
    """Collect diagnostics for the Function Codes plugin."""
    return [
        _plugin_version_result(),
        _plugin_models_result(),
        _assignment_ui_routes_result(),
        _extended_ui_routes_result(),
        _jobs_module_result(),
        _assignment_list_http_result(),
    ]


# Backward-compatible alias for the management command module path.
collect_device_integration_diagnostics = collect_plugin_diagnostics
