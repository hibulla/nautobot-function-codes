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
    path(
        "function-codes/<uuid:pk>/assign-devices/",
        views.FunctionCodeAssignDevicesView.as_view(),
        name="functioncode_assign_devices",
    ),
]

urlpatterns += router.urls
