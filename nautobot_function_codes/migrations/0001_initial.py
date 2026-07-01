"""Initial database schema for nautobot_function_codes."""

import uuid

import django.core.serializers.json
import django.db.models.deletion
import nautobot.core.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("dcim", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="FunctionCode",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                (
                    "color",
                    nautobot.core.models.fields.ColorField(blank=True, default="#9e9e9e", max_length=6),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Function Code",
                "verbose_name_plural": "Function Codes",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DeviceFunctionCodeAssignment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "device",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="function_code_assignment",
                        to="dcim.device",
                    ),
                ),
                (
                    "function_code",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="device_assignments",
                        to="nautobot_function_codes.functioncode",
                    ),
                ),
            ],
            options={
                "verbose_name": "Device Function Code Assignment",
                "verbose_name_plural": "Device Function Code Assignments",
            },
        ),
    ]
