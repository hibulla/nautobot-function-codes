"""Forms for nautobot_function_codes."""

from django import forms
from nautobot.apps.forms import (
    DynamicModelChoiceField,
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
    SlugField,
)

from nautobot_function_codes import models

__all__ = (
    "DeviceBulkEditFunctionCodeFormMixin",
    "DeviceFunctionCodeFormMixin",
    "FunctionCodeBulkEditForm",
    "FunctionCodeFilterForm",
    "FunctionCodeForm",
)


class FunctionCodeForm(NautobotModelForm):
    """FunctionCode create/edit form."""

    slug = SlugField()

    class Meta:
        """Meta attributes."""

        model = models.FunctionCode
        fields = "__all__"


class FunctionCodeBulkEditForm(NautobotBulkEditForm):
    """FunctionCode bulk edit form."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.FunctionCode.objects.all(),
        widget=forms.MultipleHiddenInput,
    )
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    color = forms.CharField(required=False)
    is_active = forms.NullBooleanField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
            "color",
            "is_active",
        ]


class FunctionCodeFilterForm(NautobotFilterForm):
    """Filter form for FunctionCode list views."""

    model = models.FunctionCode
    field_order = ["q", "name", "slug", "is_active"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search by name, slug, or description.",
    )
    name = forms.CharField(required=False, label="Name")
    slug = forms.CharField(required=False, label="Slug")
    is_active = forms.NullBooleanField(required=False, label="Active")


class DeviceFunctionCodeFormMixin(forms.Form):
    """Mixin adding Function Code selection to Device forms."""

    function_code = DynamicModelChoiceField(
        queryset=models.FunctionCode.objects.filter(is_active=True),
        required=False,
        label="Function Code",
    )

    def __init__(self, *args, **kwargs):
        """Initialize the form and pre-populate the current Function Code assignment."""
        super().__init__(*args, **kwargs)
        if self.instance is None or not self.instance.present_in_database:
            return

        try:
            assignment = self.instance.function_code_assignment
        except models.DeviceFunctionCodeAssignment.DoesNotExist:
            assignment = None

        if assignment is not None and assignment.function_code_id:
            self.initial["function_code"] = assignment.function_code_id


class DeviceBulkEditFunctionCodeFormMixin(forms.Form):
    """Mixin adding Function Code bulk edit to Device forms."""

    function_code = DynamicModelChoiceField(
        queryset=models.FunctionCode.objects.filter(is_active=True),
        required=False,
        label="Function Code",
    )
