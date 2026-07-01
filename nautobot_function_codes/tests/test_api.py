"""Unit tests for nautobot_function_codes API."""

from nautobot.apps.testing import APIViewTestCases

from nautobot_function_codes import models
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device


class FunctionCodeAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the FunctionCode API viewset."""

    model = models.FunctionCode
    choices_fields = ()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        fixtures.create_functioncode()
        cls.create_data = [
            {
                "name": "API Test One",
                "slug": "api-test-one",
                "description": "Test One Description",
            },
            {
                "name": "API Test Two",
                "slug": "api-test-two",
                "description": "Test Two Description",
            },
            {
                "name": "API Test Three",
                "slug": "api-test-three",
                "description": "Test Three Description",
            },
        ]
        cls.update_data = {
            "name": "Update Test Two",
            "slug": "update-test-two",
            "description": "Test Two Description",
        }
        cls.bulk_update_data = {
            "description": "Test Bulk Update Description",
            "is_active": True,
        }


class DeviceFunctionCodeAssignmentAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the DeviceFunctionCodeAssignment API viewset."""

    model = models.DeviceFunctionCodeAssignment
    choices_fields = ()
    brief_fields = ["id", "url", "display", "device", "function_code"]
    validation_excluded_fields = []

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.function_codes = [
            fixtures.create_functioncode_with(name="COR", slug="cor"),
            fixtures.create_functioncode_with(name="DIS", slug="dis-api"),
            fixtures.create_functioncode_with(name="ACC", slug="acc-api"),
        ]
        cls.devices = [
            create_test_device(name="api-device-1"),
            create_test_device(name="api-device-2"),
            create_test_device(name="api-device-3"),
        ]
        for device, function_code in zip(cls.devices, cls.function_codes, strict=True):
            models.DeviceFunctionCodeAssignment.objects.create(device=device, function_code=function_code)

        cls.create_devices = [
            create_test_device(name="api-device-create-1"),
            create_test_device(name="api-device-create-2"),
            create_test_device(name="api-device-create-3"),
        ]
        cls.create_data = [
            {
                "device": cls.create_devices[0].pk,
                "function_code": cls.function_codes[0].pk,
            },
            {
                "device": cls.create_devices[1].pk,
                "function_code": cls.function_codes[1].pk,
            },
            {
                "device": cls.create_devices[2].pk,
                "function_code": cls.function_codes[2].pk,
            },
        ]
        cls.update_data = {
            "function_code": cls.function_codes[0].pk,
        }
