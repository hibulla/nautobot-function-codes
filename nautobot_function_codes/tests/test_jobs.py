"""Tests for Function Code jobs."""

from django.core.files.uploadedfile import SimpleUploadedFile
from nautobot.apps.testing import TestCase, create_job_result_and_run_job

from nautobot_function_codes.jobs import jobs as jobs_module
from nautobot_function_codes.tests import fixtures
from nautobot_function_codes.tests.utils import create_test_device, get_test_job_model
from nautobot_function_codes.utils import get_device_function_code, set_device_function_code


class FunctionCodeJobsTest(TestCase):
    """Test plugin-provided Nautobot jobs."""

    user_permissions = (
        "dcim.view_device",
        "dcim.change_device",
        "nautobot_function_codes.view_functioncode",
    )

    @classmethod
    def setUpTestData(cls):
        for job_class in jobs_module.jobs:
            get_test_job_model(job_class)
        cls.function_code = fixtures.create_functioncode_with(name="ACC", slug="acc-jobs")
        cls.device = create_test_device(name="jobs-device")

    def test_audit_job_runs_successfully(self):
        set_device_function_code(self.device, self.function_code)
        job_result = create_job_result_and_run_job(
            "nautobot_function_codes.jobs.jobs",
            "AuditFunctionCodeAssignments",
            username=self.user.username,
            include_inactive_codes=True,
        )
        self.assertJobResultStatus(job_result)
        log_messages = list(job_result.job_log_entries.values_list("message", flat=True))
        self.assertTrue(any("Audit complete" in message for message in log_messages))

    def test_import_job_runs_successfully(self):
        csv_content = f"device,function_code\n{self.device.name},acc-jobs\n".encode()
        job_result = create_job_result_and_run_job(
            "nautobot_function_codes.jobs.jobs",
            "ImportFunctionCodeAssignments",
            username=self.user.username,
            csv_file=SimpleUploadedFile("assignments.csv", csv_content, content_type="text/csv"),
            dry_run=False,
        )
        self.assertJobResultStatus(job_result)
        log_messages = list(job_result.job_log_entries.values_list("message", flat=True))
        self.assertTrue(any("updated=1" in message for message in log_messages))
        self.assertEqual(get_device_function_code(self.device), self.function_code)
