"""Device integration tests."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from nautobot.apps.testing import TestCase

from nautobot_function_codes import models
from nautobot_function_codes.filter_extensions import DeviceFilterExtension
from nautobot_function_codes.forms.device import DeviceFormWithFunctionCode
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device
from nautobot_function_codes.utils import get_device_function_code, set_device_function_code


class DeviceFunctionCodeIntegrationTest(TestCase):
    """Test Device assignment helpers and filter extension field naming."""

    @classmethod
    def setUpTestData(cls):
        cls.function_code = fixtures.create_functioncode_with(name="DIS", slug="dis")
        cls.device = create_test_device(name="integration-device")
        user_model = get_user_model()
        if not user_model.objects.filter(is_superuser=True).exists():
            user_model.objects.create_superuser("integration", "integration@example.com", "password")
        cls.user = user_model.objects.filter(is_superuser=True).first()

    def test_set_and_get_device_function_code(self):
        set_device_function_code(self.device, self.function_code)
        self.assertEqual(get_device_function_code(self.device), self.function_code)

    def test_device_filter_extension_field_prefix(self):
        self.assertIn("nautobot_function_codes_function_code", DeviceFilterExtension.filterset_fields)

    def test_assignment_deleted_with_device(self):
        set_device_function_code(self.device, self.function_code)
        device_pk = self.device.pk
        self.device.delete()
        self.assertFalse(models.DeviceFunctionCodeAssignment.objects.filter(device_id=device_pk).exists())


class DeviceEditViewIntegrationTest(TestCase):
    """HTTP-level tests for Device UI integration."""

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device(name="edit-view-device")
        user_model = get_user_model()
        if not user_model.objects.filter(is_superuser=True).exists():
            user_model.objects.create_superuser("edit-view", "edit-view@example.com", "password")
        cls.user = user_model.objects.filter(is_superuser=True).first()

    def setUp(self):
        self.client.force_login(self.user)

    def test_device_edit_view_returns_200(self):
        """Regression test for present_in_database 500 on Device edit."""
        url = reverse("dcim:device_edit", kwargs={"pk": self.device.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.content[:500])

    def test_device_edit_view_shows_function_code_field(self):
        url = reverse("dcim:device_edit", kwargs={"pk": self.device.pk})
        response = self.client.get(url)
        self.assertContains(response, 'name="function_code"')
        self.assertContains(response, "Function Code")

    def test_device_add_view_shows_function_code_field(self):
        url = reverse("dcim:device_add")
        response = self.client.get(url)
        self.assertContains(response, 'name="function_code"')

    def test_device_add_view_returns_200(self):
        url = reverse("dcim:device_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.content[:500])

    def test_device_form_class_is_extended(self):
        from nautobot.dcim.views import DeviceUIViewSet

        self.assertIs(DeviceUIViewSet.form_class, DeviceFormWithFunctionCode)

    def test_device_create_template_is_extended(self):
        from nautobot.dcim.views import DeviceUIViewSet

        from nautobot_function_codes.views.device_overrides import get_device_create_template_name

        view = DeviceUIViewSet()
        view.action = "update"
        self.assertEqual(view.get_template_name(), get_device_create_template_name())
