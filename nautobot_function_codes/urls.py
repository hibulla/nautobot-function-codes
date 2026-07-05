"""Django urlpatterns declaration for nautobot_function_codes app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from nautobot_function_codes import views

app_name = "nautobot_function_codes"
router = NautobotUIViewSetRouter()

router.register("function-codes", views.FunctionCodeUIViewSet)
router.register("device-assignments", views.DeviceFunctionCodeAssignmentUIViewSet)


urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("nautobot_function_codes/docs/index.html")), name="docs"),
    path("coverage/", views.CoverageDashboardView.as_view(), name="coverage_dashboard"),
    path("import-assignments/", views.ImportAssignmentsView.as_view(), name="import_assignments"),
    path(
        "device-assignments/clear/",
        views.ClearDeviceFunctionCodeAssignmentsView.as_view(),
        name="devicefunctioncodeassignment_clear",
    ),
    path(
        "function-codes/<uuid:pk>/assign-devices/",
        views.FunctionCodeAssignDevicesView.as_view(),
        name="functioncode_assign_devices",
    ),
    path(
        "devices/<uuid:pk>/function-code/",
        views.DeviceSetFunctionCodeView.as_view(),
        name="device_set_function_code",
    ),
]

urlpatterns += router.urls
