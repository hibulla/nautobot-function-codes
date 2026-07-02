# Nautobot Function Codes

A Nautobot plugin for managing reusable Function Codes and assigning them to devices.

## Features

- Create and manage Function Codes (name, slug, description, color, active status)
- Assign exactly one Function Code to each device via the native Device form
- REST API and GraphQL support
- Global and list search, filtering, and CSV import/export
- Object permissions, changelog, notes, custom fields, relationships, custom links, and webhooks
- Device list filtering by Function Code

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

## Device Integration Notes

This plugin extends the native Device create, edit, and bulk edit forms by patching
the shared `DeviceUIViewSet` class (form class, save hooks, and edit routing guard).
It does **not** register `override_views` for `dcim:device_*` URLs, so it does not
compete with other plugins for Device route ownership.

If another plugin replaces `dcim:device_edit` with a view class other than
`DeviceUIViewSet`, the Function Code field will not appear on that custom form.

Run diagnostics after deployment:

```bash
nautobot-server diagnose_nautobot_function_codes --device-pk <uuid>
```

## Tags

Function Codes use Nautobot's `OrganizationalModel` base class (similar to Roles and Platforms). Tags are supported on `Device` objects, not on Function Code records.

## License

Apache 2.0
