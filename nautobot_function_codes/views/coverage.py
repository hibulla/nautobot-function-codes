"""Coverage dashboard views."""

from django.views.generic import TemplateView
from nautobot.core.views.mixins import ObjectPermissionRequiredMixin

from nautobot_function_codes import models
from nautobot_function_codes.services.coverage import get_coverage_stats


class CoverageDashboardView(ObjectPermissionRequiredMixin, TemplateView):
    """Show Function Code assignment coverage metrics."""

    template_name = "nautobot_function_codes/coverage_dashboard.html"
    queryset = models.FunctionCode.objects.all()

    def get_required_permission(self):
        """Require permission to view Function Codes."""
        return "nautobot_function_codes.view_functioncode"

    def get_context_data(self, **kwargs):
        """Add coverage statistics to the template context."""
        context = super().get_context_data(**kwargs)
        context["stats"] = get_coverage_stats(self.request.user)
        return context
