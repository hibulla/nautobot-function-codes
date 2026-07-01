"""FunctionCode model."""

from django.db import models
from django.urls import reverse
from nautobot.apps.constants import CHARFIELD_MAX_LENGTH
from nautobot.apps.models import OrganizationalModel, extras_features
from nautobot.core.choices import ColorChoices
from nautobot.core.models.fields import ColorField


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class FunctionCode(OrganizationalModel):
    """Operational function classification for network devices."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    slug = models.SlugField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    description = models.TextField(blank=True)
    color = ColorField(default=ColorChoices.COLOR_GREY, blank=True)
    is_active = models.BooleanField(default=True)

    natural_key_field_names = ["slug"]

    class Meta:
        """Meta attributes."""

        ordering = ["name"]
        verbose_name = "Function Code"
        verbose_name_plural = "Function Codes"

    def __str__(self):
        """Stringify instance."""
        return self.name

    def get_absolute_url(self):
        """Return the URL to the FunctionCode detail view."""
        return reverse("plugins:nautobot_function_codes:functioncode", kwargs={"pk": self.pk})
