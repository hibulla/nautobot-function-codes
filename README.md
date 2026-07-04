# Nautobot Function Codes

A Nautobot plugin for managing reusable Function Codes and assigning them to devices.

## Features

- Create and manage Function Codes (name, slug, description, active status)
- Assign devices to Function Codes via bulk Assign Devices (from Function Code detail or Device Assignments)
- Device Assignments list for view, edit, bulk edit, and delete
- Function Code column on the Device list and editable panel on Device detail pages
- Coverage dashboard with assignment statistics and links to unassigned devices
- Synchronous CSV import of device assignments from the plugin UI
- Nautobot Jobs for assignment audit and CSV import (requires Celery worker)
- REST API and GraphQL support
- Global and list search, filtering, and CSV import/export
- Object permissions, changelog, notes, custom fields, relationships, custom links, and webhooks
- Device list filtering by Function Code and by whether a device has a Function Code assigned

## Installation

```bash
pip install nautobot-function-codes
```

Add the plugin to your Nautobot configuration:

```python
PLUGINS = ["nautobot_function_codes"]
```

Run database migrations:

```bash
nautobot-server migrate nautobot_function_codes
```

## Compatibility

| Nautobot | Plugin |
|----------|--------|
| 3.1.x    | 0.2.x  |

## Development

This project uses the [cookiecutter-nautobot-app](https://github.com/nautobot/cookiecutter-nautobot-app) development environment.

```bash
poetry install
invoke makemigrations
invoke start
invoke unittest
```

## Managing Device Assignments

Device assignments are managed from the **Function Codes** plugin UI:

1. **Function Code detail → Assign Devices** — assign many devices to that Function Code
2. **Function Codes → Device Assignments → Add** — same bulk form with Function Code and Devices fields
3. **Function Codes → Device Assignments** — list, edit, bulk edit, and delete existing assignments
4. **Function Code detail → Assigned Devices** — view devices already linked to a Function Code
5. **Device detail → Function Code** — view or update the assignment for a single device
6. **Function Codes → Coverage** — review assignment coverage and open unassigned devices
7. **Function Codes → Import Assignments** — upload a CSV file and apply assignments synchronously

The REST API endpoint `/api/plugins/function-codes/device-assignments/` is also available for automation.

### CSV Import

Required columns:

```csv
device,function_code
switch-01,acc
switch-02,
```

Use the device name or UUID. Leave `function_code` empty to clear an assignment.

### Jobs

The plugin registers two Nautobot Jobs:

- **Audit Function Code Assignments** — report unassigned devices and inactive assignments
- **Import Function Code Assignments** — import assignments from CSV via the job engine

These jobs require a running Celery worker. The Coverage dashboard and Import Assignments UI work without Celery.

Run diagnostics after deployment:

```bash
nautobot-server diagnose_nautobot_function_codes
```

## Tags

Function Codes use Nautobot's `OrganizationalModel` base class (similar to Roles and Platforms). Tags are supported on `Device` objects, not on Function Code records.

## License

Apache 2.0
