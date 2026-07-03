"""Views for Device Function Code assignments."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.forms import restrict_form_fields
from nautobot.core.utils.requests import normalize_querydict
from nautobot.core.views.mixins import GetReturnURLMixin, ObjectPermissionRequiredMixin

from nautobot_function_codes import filters, models, tables
from nautobot_function_codes.api import serializers
from nautobot_function_codes.forms.assignment import (
    BulkAssignDevicesForm,
    DeviceFunctionCodeAssignmentBulkEditForm,
    DeviceFunctionCodeAssignmentFilterForm,
    DeviceFunctionCodeAssignmentForm,
    FunctionCodeAssignDevicesForm,
)
from nautobot_function_codes.utils import assign_devices_to_function_code

ASSIGN_DEVICES_TEMPLATE = "nautobot_function_codes/assign_devices.html"


def _assign_devices_and_message(request, function_code, devices):
    """Assign devices to a Function Code and add a success message."""
    assign_devices_to_function_code(function_code, devices)
    messages.success(
        request,
        f"Assigned {len(devices)} device(s) to Function Code {function_code.name}.",
    )


class DeviceFunctionCodeAssignmentUIViewSet(NautobotUIViewSet):
    """ViewSet for Device Function Code assignment CRUD views."""

    action_buttons = ("add", "export")
    bulk_update_form_class = DeviceFunctionCodeAssignmentBulkEditForm
    create_form_class = BulkAssignDevicesForm
    filterset_class = filters.DeviceFunctionCodeAssignmentFilterSet
    filterset_form_class = DeviceFunctionCodeAssignmentFilterForm
    form_class = DeviceFunctionCodeAssignmentForm
    lookup_field = "pk"
    queryset = models.DeviceFunctionCodeAssignment.objects.select_related("device", "function_code")
    serializer_class = serializers.DeviceFunctionCodeAssignmentSerializer
    table_class = tables.DeviceFunctionCodeAssignmentTable

    def perform_create(self, request, *args, **kwargs):
        """Create assignments in bulk instead of one device at a time."""
        form_class = self.get_form_class()
        form = form_class(
            data=request.POST,
            files=request.FILES,
            initial=normalize_querydict(request.GET, form_class=form_class),
        )
        restrict_form_fields(form, request.user)
        if not form.is_valid():
            return self.form_invalid(form)

        function_code = form.cleaned_data["function_code"]
        devices = form.cleaned_data["devices"]
        _assign_devices_and_message(request, function_code, devices)

        return_url = self.get_return_url(request)
        if not return_url:
            return_url = reverse("plugins:nautobot_function_codes:devicefunctioncodeassignment_list")
        return redirect(return_url)


class FunctionCodeAssignDevicesView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """Assign multiple devices to a single Function Code (Function Code fixed by URL)."""

    template_name = ASSIGN_DEVICES_TEMPLATE
    queryset = models.FunctionCode.objects.all()

    def get_required_permission(self):
        """Require permission to change Function Code assignments."""
        return "nautobot_function_codes.change_functioncode"

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
        _assign_devices_and_message(request, function_code, devices)
        return redirect(return_url)
