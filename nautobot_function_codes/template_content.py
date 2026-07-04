"""Template extensions for Device integration."""

from django.urls import reverse
from nautobot.apps.ui import Panel, SectionChoices, TemplateExtension

from nautobot_function_codes.forms.device import DeviceFunctionCodePanelForm
from nautobot_function_codes.utils import get_device_function_code


class FunctionCodeDetailPanel(Panel):
    """Detail panel showing and editing the assigned Function Code."""

    def __init__(self, **kwargs):
        """Initialize the Function Code detail panel."""
        super().__init__(
            body_content_template_path="nautobot_function_codes/inc/function_code_panel.html",
            label="Function Code",
            weight=120,
            section=SectionChoices.RIGHT_HALF,
            **kwargs,
        )

    def get_extra_context(self, context):
        """Return Function Code context for the panel template."""
        device = context["object"]
        function_code = get_device_function_code(device)
        request = context["request"]
        can_change = request.user.has_perm("nautobot_function_codes.change_functioncode")
        panel_form = DeviceFunctionCodePanelForm(initial={"function_code": function_code.pk if function_code else None})
        return {
            "function_code": function_code,
            "can_change_function_code": can_change,
            "panel_form": panel_form,
            "set_function_code_url": reverse(
                "plugins:nautobot_function_codes:device_set_function_code",
                kwargs={"pk": device.pk},
            ),
        }


class DeviceFunctionCodeTemplateExtension(TemplateExtension):
    """Extend Device detail views with Function Code information."""

    model = "dcim.device"
    object_detail_panels = (FunctionCodeDetailPanel(),)


template_extensions = [DeviceFunctionCodeTemplateExtension]
