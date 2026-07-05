"""Views for Device Function Code assignments."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.forms import restrict_form_fields
from nautobot.core.utils.requests import normalize_querydict
from nautobot.core.views.mixins import (
    ContentTypePermissionRequiredMixin,
    GetReturnURLMixin,
)

from nautobot_function_codes import filters, models, tables
from nautobot_function_codes.api import serializers
from nautobot_function_codes.forms.assignment import (
    BulkAssignDevicesForm,
    ClearDeviceFunctionCodeAssignmentsForm,
    DeviceFunctionCodeAssignmentBulkEditForm,
    DeviceFunctionCodeAssignmentFilterForm,
    DeviceFunctionCodeAssignmentForm,
    FunctionCodeAssignDevicesForm,
)
from nautobot_function_codes.utils import assign_devices_to_function_code, unassign_devices

ASSIGN_DEVICES_TEMPLATE = "nautobot_function_codes/assign_devices.html"
CLEAR_ASSIGNMENTS_TEMPLATE = "nautobot_function_codes/clear_assignments.html"


def _assign_devices_and_message(request, function_code, devices):
    """Assign devices to a Function Code and add a success message."""
    try:
        assign_devices_to_function_code(function_code, devices)
    except ValidationError as exc:
        message = exc.message_dict.get("function_code", exc.messages)
        if isinstance(message, list):
            message = message[0]
        messages.error(request, message)
        return False

    messages.success(
        request,
        f"Assigned {len(devices)} device(s) to Function Code {function_code.name}.",
    )
    return True


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

    def send_bulk_edit_objects_to_job(self, request, form_data):
        """Apply bulk edit synchronously instead of enqueueing a Celery job."""
        model = self.get_queryset().model
        edit_all = bool(request.POST.get("_all"))
        form = self.get_form_class()(model, request.POST, edit_all=edit_all)
        restrict_form_fields(form, request.user)
        if not form.is_valid():
            return self.form_invalid(form)

        self._process_bulk_update_form(form)
        return redirect(self.get_return_url(request))

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
        if not _assign_devices_and_message(request, function_code, devices):
            return self.form_invalid(form)

        return_url = self.get_return_url(request)
        if not return_url:
            return_url = reverse("plugins:nautobot_function_codes:devicefunctioncodeassignment_list")
        return redirect(return_url)


class FunctionCodeAssignDevicesView(GetReturnURLMixin, ContentTypePermissionRequiredMixin, View):
    """Assign multiple devices to a single Function Code (Function Code fixed by URL)."""

    template_name = ASSIGN_DEVICES_TEMPLATE
    queryset = models.FunctionCode.objects.all()

    def get_required_permission(self):
        """Require permission to change Function Code assignments."""
        return "nautobot_function_codes.change_devicefunctioncodeassignment"

    def get(self, request, pk):
        """Render the bulk assignment form."""
        function_code = get_object_or_404(self.queryset, pk=pk)
        if not function_code.is_active:
            messages.error(
                request, f"Function Code '{function_code.name}' is inactive and cannot receive new assignments."
            )
            return redirect(function_code.get_absolute_url())

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
        function_code = get_object_or_404(self.queryset, pk=pk)
        return_url = self.get_return_url(request, obj=function_code)

        if not function_code.is_active:
            messages.error(
                request, f"Function Code '{function_code.name}' is inactive and cannot receive new assignments."
            )
            return redirect(return_url)

        form = FunctionCodeAssignDevicesForm(request.POST)

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


class ClearDeviceFunctionCodeAssignmentsView(GetReturnURLMixin, ContentTypePermissionRequiredMixin, View):
    """Clear Function Code assignments for one or more devices."""

    template_name = CLEAR_ASSIGNMENTS_TEMPLATE
    queryset = models.DeviceFunctionCodeAssignment.objects.all()

    def get_required_permission(self):
        """Require permission to change assignment records."""
        return "nautobot_function_codes.change_devicefunctioncodeassignment"

    def get(self, request):
        """Render the clear assignments form."""
        form = ClearDeviceFunctionCodeAssignmentsForm()
        restrict_form_fields(form, request.user)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "return_url": self.get_return_url(request),
            },
        )

    def post(self, request):
        """Clear the selected devices' Function Code assignments."""
        form = ClearDeviceFunctionCodeAssignmentsForm(request.POST)
        restrict_form_fields(form, request.user)
        return_url = self.get_return_url(request)

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "return_url": return_url,
                },
            )

        devices = form.cleaned_data["devices"]
        unassign_devices(devices)
        messages.success(request, f"Cleared Function Code assignment for {len(devices)} device(s).")
        if not return_url:
            return_url = reverse("plugins:nautobot_function_codes:devicefunctioncodeassignment_list")
        return redirect(return_url)
