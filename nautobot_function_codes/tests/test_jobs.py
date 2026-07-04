"""Tests for Function Code jobs."""

from django.core.files.uploadedfile import SimpleUploadedFile
from nautobot.apps.testing import TestCase

from nautobot_function_codes.jobs.jobs import AuditFunctionCodeAssignments, ImportFunctionCodeAssignments
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device
from nautobot_function_codes.utils import get_device_function_code, set_device_function_code


class FunctionCodeJobsTest(TestCase):
    """Test plugin-provided Nautobot jobs."""

    @classmethod
    def setUpTestData(cls):
        cls.function_code = fixtures.create_functioncode_with(name="ACC", slug="acc-jobs")
        cls.device = create_test_device(name="jobs-device")

    def test_audit_job_runs_successfully(self):
        set_device_function_code(self.device, self.function_code)
        job = AuditFunctionCodeAssignments()
        job.user = self.user
        job.include_inactive_codes = True
        summary = job.run()
        self.assertIn("Audit complete", summary)

    def test_import_job_runs_successfully(self):
        csv_content = f"device,function_code\n{self.device.name},acc-jobs\n".encode()
        job = ImportFunctionCodeAssignments()
        job.user = self.user
        job.csv_file = SimpleUploadedFile("assignments.csv", csv_content, content_type="text/csv")
        job.dry_run = False
        summary = job.run()
        self.assertIn("updated=1", summary)
        self.assertEqual(get_device_function_code(self.device), self.function_code)
