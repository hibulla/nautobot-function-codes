"""Diagnostics tests."""

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from nautobot.apps.testing import TestCase
from nautobot.dcim.views import DeviceUIViewSet

from nautobot_function_codes.diagnostics import collect_device_integration_diagnostics
from nautobot_function_codes.tests.utils import create_test_device


class DeviceIntegrationDiagnosticsTest(TestCase):
    """Test Device integration diagnostic helpers."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        if not user_model.objects.filter(is_superuser=True).exists():
            user_model.objects.create_superuser("diagnostics", "diagnostics@example.com", "password")
        cls.device = create_test_device(name="diagnostics-device")
        cls.user = user_model.objects.filter(is_superuser=True).first()

    def test_collect_device_integration_diagnostics_passes(self):
        results = collect_device_integration_diagnostics()
        checks = {result.check: result for result in results}

        self.assertEqual(checks["integration_state"].status, "ok")
        self.assertEqual(checks["device_form_class"].status, "ok")
        self.assertEqual(checks["device_initialize_request"].status, "ok")
        self.assertIn(checks["url_dcim_device_edit"].status, ("ok", "warning"))

    def test_collect_device_integration_diagnostics_with_device_pk(self):
        results = collect_device_integration_diagnostics(device_pk=self.device.pk)
        checks = {result.check: result for result in results}

        self.assertIn("device_get_object", checks)
        self.assertEqual(checks["device_get_object"].status, "ok", checks["device_get_object"].message)

    def test_device_get_object_via_initialize_request(self):
        request = RequestFactory().get(f"/dcim/devices/{self.device.pk}/edit/")
        request.user = self.user

        viewset = DeviceUIViewSet()
        viewset.action_map = {"get": "update"}
        viewset.kwargs = {"pk": str(self.device.pk)}
        viewset.detail = False
        viewset.request = viewset.initialize_request(request, pk=str(self.device.pk))

        self.assertTrue(viewset.detail)
        instance = viewset.get_object()
        self.assertEqual(instance.pk, self.device.pk)

    def test_device_update_initialize_request_forces_detail(self):
        request = RequestFactory().get(f"/dcim/devices/{self.device.pk}/edit/")
        request.user = self.user

        viewset = DeviceUIViewSet()
        viewset.action_map = {"get": "update"}
        viewset.detail = False
        viewset.initialize_request(request, pk=str(self.device.pk))

        self.assertEqual(viewset.action, "update")
        self.assertTrue(viewset.detail)
