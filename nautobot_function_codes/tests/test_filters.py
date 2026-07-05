"""Test FunctionCode filters."""

from nautobot.apps.testing import FilterTestCases, TestCase

from nautobot_function_codes import filters, models
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device


class FunctionCodeFilterTestCase(FilterTestCases.FilterTestCase):
    """FunctionCode Filter Test Case."""

    queryset = models.FunctionCode.objects.all()
    filterset = filters.FunctionCodeFilterSet
    generic_filter_tests = (
        ("id",),
        ("created",),
        ("last_updated",),
        ("name",),
        ("slug",),
    )

    @classmethod
    def setUpTestData(cls):
        fixtures.create_functioncode()

    def test_q_search_name(self):
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_search_slug(self):
        params = {"q": "test-two"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_search_description(self):
        code = fixtures.create_functioncode_with(
            name="Searchable",
            slug="searchable",
            description="unique-search-term",
        )
        params = {"q": "unique-search-term"}
        self.assertIn(code, self.filterset(params, self.queryset).qs)

    def test_q_invalid(self):
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_is_active_filter(self):
        active_code = fixtures.create_functioncode_with(name="Active Code", slug="active-code", is_active=True)
        inactive_code = fixtures.create_functioncode_with(name="Inactive Code", slug="inactive-code", is_active=False)

        self.assertIn(active_code, self.filterset({"is_active": True}, self.queryset).qs)
        self.assertIn(inactive_code, self.filterset({"is_active": False}, self.queryset).qs)
        self.assertNotIn(inactive_code, self.filterset({"is_active": True}, self.queryset).qs)


class DeviceFunctionCodeAssignmentFilterTestCase(TestCase):
    """DeviceFunctionCodeAssignment Filter Test Case."""

    queryset = models.DeviceFunctionCodeAssignment.objects.all()
    filterset = filters.DeviceFunctionCodeAssignmentFilterSet

    @classmethod
    def setUpTestData(cls):
        cls.active_code = fixtures.create_functioncode_with(name="Assignment Active", slug="assignment-active")
        cls.inactive_code = fixtures.create_functioncode_with(
            name="Assignment Inactive",
            slug="assignment-inactive",
            is_active=False,
        )
        cls.active_assignment = models.DeviceFunctionCodeAssignment.objects.create(
            device=create_test_device(name="filter-assignment-active"),
            function_code=cls.active_code,
        )
        cls.inactive_assignment = models.DeviceFunctionCodeAssignment.objects.create(
            device=create_test_device(name="filter-assignment-inactive"),
            function_code=cls.inactive_code,
        )

    def test_function_code_is_active_filter(self):
        active_results = self.filterset({"function_code_is_active": True}, self.queryset).qs
        inactive_results = self.filterset({"function_code_is_active": False}, self.queryset).qs

        self.assertIn(self.active_assignment, active_results)
        self.assertNotIn(self.inactive_assignment, active_results)
        self.assertIn(self.inactive_assignment, inactive_results)
        self.assertNotIn(self.active_assignment, inactive_results)
