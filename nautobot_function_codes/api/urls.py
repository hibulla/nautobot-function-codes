"""API URL patterns for nautobot_function_codes."""

from nautobot.apps.api import OrderedDefaultRouter

from nautobot_function_codes.api import views

router = OrderedDefaultRouter()
router.register("function-codes", views.FunctionCodeViewSet)
router.register("device-assignments", views.DeviceFunctionCodeAssignmentViewSet)

app_name = "nautobot-function-codes-api"
urlpatterns = router.urls
