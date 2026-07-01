"""Template extensions for Device integration."""

from nautobot.apps.ui import Panel, SectionChoices, TemplateExtension

from nautobot_function_codes.utils import get_device_function_code


class FunctionCodeDetailPanel(Panel):
    """Detail panel showing the assigned Function Code."""

    def __init__(self, **kwargs):
        super().__init__(
            body_content_template_path="nautobot_function_codes/inc/function_code_panel.html",
            label="Function Code",
            weight=120,
            section=SectionChoices.RIGHT_HALF,
            **kwargs,
        )

    def get_extra_context(self, context):
        return {"function_code": get_device_function_code(context["object"])}


class DeviceFunctionCodeTemplateExtension(TemplateExtension):
    """Extend Device detail views with Function Code information."""

    model = "dcim.device"
    object_detail_panels = (FunctionCodeDetailPanel(),)


template_extensions = [DeviceFunctionCodeTemplateExtension]
