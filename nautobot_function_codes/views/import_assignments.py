"""Views for CSV import of device assignments."""

import csv

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from nautobot.core.forms import restrict_form_fields
from nautobot.core.views.mixins import ContentTypePermissionRequiredMixin
from nautobot.dcim.models import Device

from nautobot_function_codes import models
from nautobot_function_codes.forms.import_assignments import ImportAssignmentsForm
from nautobot_function_codes.services.import_assignments import import_assignments_from_csv


def _assignment_csv_response(filename):
    """Return an HTTP CSV response with assignment headers."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(["device", "function_code"])
    return response, writer


class ImportAssignmentsView(ContentTypePermissionRequiredMixin, View):
    """Synchronously import device Function Code assignments from CSV."""

    template_name = "nautobot_function_codes/import_assignments.html"
    queryset = models.DeviceFunctionCodeAssignment.objects.all()

    def get_required_permission(self):
        """Require permission to change Function Code assignments."""
        return "nautobot_function_codes.change_devicefunctioncodeassignment"

    def get(self, request):
        """Render the CSV upload form."""
        export = request.GET.get("export")
        if export == "template":
            response, _ = _assignment_csv_response("function-code-assignments-template.csv")
            return response
        if export == "current":
            response, writer = _assignment_csv_response("function-code-assignments-current.csv")
            devices = (
                Device.objects.restrict(request.user, "view")
                .select_related("function_code_assignment__function_code")
                .order_by("name", "pk")
            )
            for device in devices:
                function_code = getattr(
                    getattr(device, "function_code_assignment", None),
                    "function_code",
                    None,
                )
                writer.writerow([device.name, function_code.slug if function_code else ""])
            return response

        return render(
            request,
            self.template_name,
            {
                "form": ImportAssignmentsForm(),
                "result": None,
                "export_template_url": f"{request.path}?export=template",
                "export_current_url": f"{request.path}?export=current",
            },
        )

    def post(self, request):
        """Process the uploaded CSV file."""
        form = ImportAssignmentsForm(request.POST, request.FILES)
        restrict_form_fields(form, request.user)

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "result": None,
                    "export_template_url": f"{request.path}?export=template",
                    "export_current_url": f"{request.path}?export=current",
                },
            )

        try:
            result = import_assignments_from_csv(
                form.cleaned_data["csv_file"],
                request.user,
                dry_run=form.cleaned_data["dry_run"],
            )
        except ValueError as exc:
            messages.error(request, str(exc))
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "result": None,
                    "export_template_url": f"{request.path}?export=template",
                    "export_current_url": f"{request.path}?export=current",
                },
            )

        if result.errors:
            messages.warning(request, f"Import completed with errors. {result.summary}")
        else:
            messages.success(request, f"Import completed successfully. {result.summary}")

        return render(
            request,
            self.template_name,
            {
                "form": ImportAssignmentsForm(initial={"dry_run": form.cleaned_data["dry_run"]}),
                "result": result,
                "export_template_url": f"{request.path}?export=template",
                "export_current_url": f"{request.path}?export=current",
            },
        )
