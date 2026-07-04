"""Device to FunctionCode assignment model."""

from django.db import models
from nautobot.apps.models import BaseModel

from nautobot_function_codes.validators import validate_function_code_for_assignment


class DeviceFunctionCodeAssignment(BaseModel):
    """Extension record linking a Device to its Function Code."""

    is_metadata_associable_model = False

    device = models.OneToOneField(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="function_code_assignment",
    )
    function_code = models.ForeignKey(
        to="nautobot_function_codes.FunctionCode",
        on_delete=models.PROTECT,
        related_name="device_assignments",
        blank=True,
        null=True,
    )

    class Meta:
        """Meta attributes."""

        verbose_name = "Device Function Code Assignment"
        verbose_name_plural = "Device Function Code Assignments"

    def __str__(self):
        """Stringify instance."""
        if self.function_code:
            return f"{self.device}: {self.function_code}"
        return f"{self.device}: (none)"

    def clean(self):
        """Validate assignment fields."""
        super().clean()
        validate_function_code_for_assignment(self.function_code)

