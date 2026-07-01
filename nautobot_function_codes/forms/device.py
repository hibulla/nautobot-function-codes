"""Device form extensions for Function Code assignment."""

from nautobot.dcim.forms import DeviceBulkEditForm, DeviceForm

from nautobot_function_codes.forms import DeviceBulkEditFunctionCodeFormMixin, DeviceFunctionCodeFormMixin


class DeviceFormWithFunctionCode(DeviceFunctionCodeFormMixin, DeviceForm):
    """Device create/edit form with Function Code field."""


class DeviceBulkEditFormWithFunctionCode(DeviceBulkEditFunctionCodeFormMixin, DeviceBulkEditForm):
    """Device bulk edit form with Function Code field."""
