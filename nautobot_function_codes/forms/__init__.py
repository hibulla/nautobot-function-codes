"""Forms for nautobot_function_codes."""

from django import forms
from nautobot.apps.forms import (
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
    SlugField,
)

from nautobot_function_codes import models
from nautobot_function_codes.forms.assignment import DeviceFunctionCodeAssignmentBulkEditForm

__all__ = (
    "DeviceFunctionCodeAssignmentBulkEditForm",
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
