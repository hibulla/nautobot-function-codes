"""Remove unused color field from FunctionCode."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_function_codes", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="functioncode",
            name="color",
        ),
    ]
