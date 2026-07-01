"""Views for FunctionCode."""

from django.db.models import Count

from nautobot.apps.ui import ObjectDetailContent, ObjectFieldsPanel, SectionChoices
from nautobot.apps.views import NautobotUIViewSet

from nautobot_function_codes import filters, forms, models, tables
from nautobot_function_codes.api import serializers


class FunctionCodeUIViewSet(NautobotUIViewSet):
    """ViewSet for FunctionCode CRUD views."""

    bulk_update_form_class = forms.FunctionCodeBulkEditForm
    filterset_class = filters.FunctionCodeFilterSet
    filterset_form_class = forms.FunctionCodeFilterForm
    form_class = forms.FunctionCodeForm
    lookup_field = "pk"
    queryset = models.FunctionCode.objects.annotate(device_count=Count("device_assignments"))
    serializer_class = serializers.FunctionCodeSerializer
    table_class = tables.FunctionCodeTable

    object_detail_content = ObjectDetailContent(
        panels=[
            ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=[
                    "name",
                    "slug",
                    "description",
                    "color",
                    "is_active",
                    "created",
                    "last_updated",
                ],
            ),
        ],
    )
