"""FunctionCode model."""

from django.db import models
from nautobot.apps.constants import CHARFIELD_MAX_LENGTH
from nautobot.apps.models import OrganizationalModel, extras_features


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
