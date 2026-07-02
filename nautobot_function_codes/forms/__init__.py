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
from nautobot_function_codes.debug_utils import debug_log

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
        instance = self.instance
        debug_log(
            "DeviceFunctionCodeFormMixin init: instance=%s present_in_database=%s pk=%s",
            type(instance).__name__ if instance is not None else None,
            getattr(instance, "present_in_database", None),
            getattr(instance, "pk", None),
        )
        if instance is None or not instance.present_in_database:
            return

        try:
            assignment = instance.function_code_assignment
        except models.DeviceFunctionCodeAssignment.DoesNotExist:
            assignment = None

        if assignment is not None and assignment.function_code_id:
            self.initial["function_code"] = assignment.function_code_id
            debug_log(
                "DeviceFunctionCodeFormMixin init: pre-filled function_code_id=%s",
                assignment.function_code_id,
            )


class DeviceBulkEditFunctionCodeFormMixin(forms.Form):
    """Mixin adding Function Code bulk edit to Device forms."""

    function_code = DynamicModelChoiceField(
        queryset=models.FunctionCode.objects.filter(is_active=True),
        required=False,
        label="Function Code",
    )
