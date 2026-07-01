"""Add custom field storage to FunctionCode."""

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_function_codes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="functioncode",
            name="_custom_field_data",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
            ),
        ),
    ]
