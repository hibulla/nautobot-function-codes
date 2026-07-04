"""Views for CSV import of device assignments."""

from django.contrib import messages
from django.shortcuts import render
from django.views import View
from nautobot.core.forms import restrict_form_fields
from nautobot.core.views.mixins import ObjectPermissionRequiredMixin

from nautobot_function_codes import models
from nautobot_function_codes.forms.import_assignments import ImportAssignmentsForm
from nautobot_function_codes.services.import_assignments import import_assignments_from_csv


class ImportAssignmentsView(ObjectPermissionRequiredMixin, View):
    """Synchronously import device Function Code assignments from CSV."""

    template_name = "nautobot_function_codes/import_assignments.html"
    queryset = models.DeviceFunctionCodeAssignment.objects.all()

    def get_required_permission(self):
        """Require permission to change Function Code assignments."""
        return "nautobot_function_codes.change_functioncode"

    def get(self, request):
        """Render the CSV upload form."""
        return render(
            request,
            self.template_name,
            {
                "form": ImportAssignmentsForm(),
                "result": None,
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
            },
        )
