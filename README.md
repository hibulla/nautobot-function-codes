# Nautobot Function Codes

A Nautobot plugin for managing reusable Function Codes and assigning them to devices.

## Features

- Create and manage Function Codes (name, slug, description, color, active status)
- Assign devices to Function Codes from the plugin UI (single device or many at once)
- Device Assignments list with create, edit, bulk edit, and delete
- REST API and GraphQL support
- Global and list search, filtering, and CSV import/export
- Object permissions, changelog, notes, custom fields, relationships, custom links, and webhooks
- Device list filtering by Function Code
- Read-only Function Code panel on Device detail pages

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
| 3.1.x    | 0.1.x  |

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

1. **Function Codes → Device Assignments** — list, create, edit, bulk edit, and delete assignments
2. **Function Code detail → Assign Devices** — assign multiple devices to one Function Code at once
3. **Function Code detail → Assigned Devices** — view devices already linked to a Function Code

The REST API endpoint `/api/plugins/function-codes/device-assignments/` is also available for automation.

Run diagnostics after deployment:

```bash
nautobot-server diagnose_nautobot_function_codes
```

## Tags

Function Codes use Nautobot's `OrganizationalModel` base class (similar to Roles and Platforms). Tags are supported on `Device` objects, not on Function Code records.

## License

Apache 2.0
