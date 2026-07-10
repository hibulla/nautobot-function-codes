# Nautobot Function Codes

A Nautobot plugin for managing reusable Function Codes and assigning them to devices.

Documentation: [docs.nautobot.com/projects/function-codes](https://docs.nautobot.com/projects/function-codes/en/latest/)

## Features

### Function Codes

- Create and manage Function Codes (`name`, `slug`, `description`, `is_active`)
- REST API and GraphQL support
- Global and list search, filtering, and CSV import/export
- Object permissions, changelog, notes, custom fields, relationships, custom links, and webhooks

### Device assignments

- One Function Code per device (via `DeviceFunctionCodeAssignment`)
- Assign devices in bulk from Function Code detail or Device Assignments
- Device Assignments list with view, edit, bulk edit, and delete
- Clear assignments in bulk from the plugin menu
- Function Code column on the Device list
- Editable Function Code panel on Device detail pages
- Validation prevents assigning inactive Function Codes

### Coverage and import

- Coverage dashboard with assignment statistics by Function Code, status, location, and role
- Links to unassigned devices and assignments that reference inactive Function Codes
- Synchronous CSV import/export from **Function Codes → Import Assignments** (no Celery required)
- Nautobot Jobs for scheduled or background audit and CSV import (requires Celery worker)

### Filtering

- Filter Device list by Function Code
- Filter Device list by whether a device has a Function Code assigned (`Has Function Code`)

## Requirements

- Nautobot 3.1.0 or higher
- Python 3.12 or higher

## Installation

Install the package from PyPI:

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

Restart Nautobot after installing and migrating the plugin.

## Compatibility

| Nautobot | Plugin | Python |
|----------|--------|--------|
| 3.1.x    | 0.1.x  | 3.12+  |

## Development

This project uses the [cookiecutter-nautobot-app](https://github.com/nautobot/cookiecutter-nautobot-app) development environment.

```bash
poetry install
invoke makemigrations
invoke start
invoke unittest
```

Other useful commands:

```bash
invoke pylint
invoke ruff
poetry run mkdocs build --no-directory-urls --strict
poetry run python -m build
poetry run python -m twine check dist/*
```

For local invoke commands that should run outside Docker, set:

```bash
export INVOKE_NAUTOBOT_FUNCTION_CODES_LOCAL=True
```

## Releasing

Releases are published to PyPI automatically when a Git tag matching `v*` is pushed.

1. Update the version in `pyproject.toml`, for example:

   ```bash
   poetry version patch
   ```

1. Update release notes or changelog content as needed.

1. Commit the release changes:

   ```bash
   git add pyproject.toml poetry.lock CHANGELOG.md docs/admin/release_notes
   git commit -m "Prepare release vX.Y.Z"
   ```

1. Create and push the tag:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

The `Release` GitHub Actions workflow builds the package with `python -m build`, verifies it with `twine check`, and publishes it to PyPI. If PyPI Trusted Publishing is configured for this repository and workflow, no API token is needed. Otherwise, add a repository or environment secret named `PYPI_API_TOKEN` containing a PyPI API token.

## Managing Device Assignments

Device assignments are managed from the **Function Codes** plugin menu:

1. **Function Codes → Function Codes** — create and manage Function Code records
2. **Function Code detail → Assign Devices** — assign many devices to one Function Code
3. **Function Codes → Device Assignments → Add** — bulk form with Function Code and Devices fields
4. **Function Codes → Device Assignments** — list, edit, bulk edit, and delete assignments
5. **Function Code detail → Assigned Devices** — view devices linked to a Function Code
6. **Device detail → Function Code** — view or update the assignment for a single device
7. **Function Codes → Coverage** — review assignment coverage and open unassigned or inactive assignments
8. **Function Codes → Import Assignments** — upload, validate, or export assignment CSV files
9. **Function Codes → Clear Assignments** — clear assignments for selected devices

### REST API

| Endpoint | Description |
|----------|-------------|
| `/api/plugins/function-codes/function-codes/` | Function Code CRUD |
| `/api/plugins/function-codes/device-assignments/` | Device assignment CRUD |

Device list filtering examples:

- `?nautobot_function_codes_function_code=acc` — devices with Function Code slug `acc`
- `?nautobot_function_codes_has_function_code=true` — devices with any Function Code assigned
- `?nautobot_function_codes_has_function_code=false` — devices without a Function Code

### CSV import format

Required columns:

```csv
device,function_code
switch-01,acc
switch-02,
```

Use the device name or UUID. Leave `function_code` empty to clear an assignment. Inactive Function Codes are rejected.

The same format is used by both **Import Assignments** (UI) and the **Import Function Code Assignments** job. The import UI can also download a blank CSV template or export the current assignment state.

### Jobs

The plugin registers two Nautobot Jobs:

- **Audit Function Code Assignments** — report unassigned devices and assignments to inactive Function Codes
- **Import Function Code Assignments** — import assignments from CSV via the job engine

Jobs require a running Celery worker. The Coverage dashboard and Import Assignments UI work without Celery.

Run diagnostics after deployment:

```bash
nautobot-server diagnose_nautobot_function_codes
```

## Tags

Function Codes use Nautobot's `OrganizationalModel` base class (similar to Roles and Platforms). Tags are supported on `Device` objects, not on Function Code records.

## About

This plugin is created and maintained by [hibulla.com](https://www.hibulla.com).
Contact: [contact@hibulla.com](mailto:contact@hibulla.com)

## License

Apache 2.0
