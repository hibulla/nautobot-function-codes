"""Django urlpatterns declaration for nautobot_function_codes app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter


from nautobot_function_codes import views


app_name = "nautobot_function_codes"
router = NautobotUIViewSetRouter()

# The standard is for the route to be the hyphenated version of the model class name plural.
# for example, ExampleModel would be example-models.
router.register("function-codes", views.FunctionCodeUIViewSet)


urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("nautobot_function_codes/docs/index.html")), name="docs"),
]

urlpatterns += router.urls
