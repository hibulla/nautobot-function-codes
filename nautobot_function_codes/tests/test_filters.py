"""Test FunctionCode filters."""

from nautobot.apps.testing import FilterTestCases

from nautobot_function_codes import filters, models
from nautobot_function_codes.tests import fixtures


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
