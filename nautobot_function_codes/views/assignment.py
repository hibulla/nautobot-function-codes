"""Views for Device Function Code assignments."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.views.mixins import GetReturnURLMixin, ObjectPermissionRequiredMixin

from nautobot_function_codes import filters, models, tables
from nautobot_function_codes.api import serializers
from nautobot_function_codes.forms.assignment import (
    DeviceFunctionCodeAssignmentBulkEditForm,
    DeviceFunctionCodeAssignmentFilterForm,
    DeviceFunctionCodeAssignmentForm,
    FunctionCodeAssignDevicesForm,
)
from nautobot_function_codes.utils import assign_devices_to_function_code


class DeviceFunctionCodeAssignmentUIViewSet(NautobotUIViewSet):
    """ViewSet for Device Function Code assignment CRUD views."""

    bulk_update_form_class = DeviceFunctionCodeAssignmentBulkEditForm
    filterset_class = filters.DeviceFunctionCodeAssignmentFilterSet
    filterset_form_class = DeviceFunctionCodeAssignmentFilterForm
    form_class = DeviceFunctionCodeAssignmentForm
    lookup_field = "pk"
    queryset = models.DeviceFunctionCodeAssignment.objects.select_related("device", "function_code")
    serializer_class = serializers.DeviceFunctionCodeAssignmentSerializer
    table_class = tables.DeviceFunctionCodeAssignmentTable


class FunctionCodeAssignDevicesView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """Assign multiple devices to a single Function Code."""

    template_name = "nautobot_function_codes/functioncode_assign_devices.html"

    def get_required_permission(self):
        """Require permission to change Function Code assignments."""
        return "nautobot_function_codes.change_devicefunctioncodeassignment"

    def get(self, request, pk):
        """Render the bulk assignment form."""
        function_code = get_object_or_404(models.FunctionCode, pk=pk)
        return render(
            request,
            self.template_name,
            {
                "function_code": function_code,
                "form": FunctionCodeAssignDevicesForm(),
                "return_url": self.get_return_url(request, obj=function_code),
            },
        )

    def post(self, request, pk):
        """Assign the selected devices to the Function Code."""
        function_code = get_object_or_404(models.FunctionCode, pk=pk)
        form = FunctionCodeAssignDevicesForm(request.POST)
        return_url = self.get_return_url(request, obj=function_code)

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "function_code": function_code,
                    "form": form,
                    "return_url": return_url,
                },
            )

        devices = form.cleaned_data["devices"]
        assign_devices_to_function_code(function_code, devices)
        messages.success(
            request,
            f"Assigned {len(devices)} device(s) to Function Code {function_code.name}.",
        )
        return redirect(return_url)
