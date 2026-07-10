# Publishing to PyPI

This page documents the repository setup required before Nautobot Function Codes can be publicly released on PyPI.

## Package Identity

The package has two names:

| Purpose | Value |
| ------- | ----- |
| PyPI package name | `nautobot-function-codes` |
| Python import package | `nautobot_function_codes` |
| Nautobot plugin name | `nautobot_function_codes` |

The canonical package metadata is defined in `pyproject.toml` using PEP 621 `[project]` metadata. Keep the README, documentation, and release notes aligned with that file.

## PyPI Project Setup

Before the first public release:

1. Create or claim the `nautobot-function-codes` project on PyPI.
2. Confirm that the project description renders correctly from `README.md`.
3. Confirm that the license is shown as `Apache-2.0`.
4. Confirm that the project links point to the GitHub repository, documentation, issue tracker, and changelog.

## Authentication

Preferred authentication is PyPI Trusted Publishing.

Configure a trusted publisher in PyPI with:

- owner: `hibulla`
- repository: `nautobot-function-codes`
- workflow: `release.yml`
- environment: `pypi`

The workflow has `id-token: write` permission and will use Trusted Publishing when `PYPI_API_TOKEN` is not configured.

If Trusted Publishing is not available, create a PyPI API token and store it in GitHub as `PYPI_API_TOKEN`. The secret can be configured either at repository level or in the `pypi` environment used by the release workflow.

## Local Package Validation

Run these commands before creating a release tag:

```shell
poetry check --lock
poetry run mkdocs build --no-directory-urls --strict
rm -rf dist
poetry run python -m build
poetry run python -m twine check dist/*
```

For a stronger local smoke test, install the built wheel into a clean virtual environment:

```shell
python3 -m venv /tmp/nautobot-function-codes-wheel-test
/tmp/nautobot-function-codes-wheel-test/bin/python -m pip install --no-deps dist/*.whl
/tmp/nautobot-function-codes-wheel-test/bin/python -m pip show nautobot-function-codes
```

## Release Trigger

The release workflow is triggered by a pushed tag:

```shell
git tag vX.Y.Z
git push origin vX.Y.Z
```

The tag must match the version in `pyproject.toml`. For example, `version = "0.1.0"` must be released with tag `v0.1.0`.

The workflow builds the package, runs `twine check`, and publishes to PyPI. It does not publish on branch pushes, pull requests, or GitHub Release events.
