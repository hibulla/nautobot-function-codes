# Release Checklist

This document is intended for maintainers preparing a public release of Nautobot Function Codes.

!!! important
    Before starting, make sure your local `develop`, `main`, and any active release branch are up to date with upstream.

    ```shell
    git fetch
    git switch develop && git pull
    git switch main && git pull
    ```

## Pre-release Checks

### Verify package metadata

Confirm that `pyproject.toml` contains the public package metadata expected by PyPI:

- package name: `nautobot-function-codes`
- import package: `nautobot_function_codes`
- author: `hibulla.com`
- license: `Apache-2.0`
- README: `README.md`
- repository URL: `https://github.com/hibulla/nautobot-function-codes`
- supported Python range
- supported Nautobot dependency range

Run:

```shell
poetry check --lock
```

### Verify documentation

Update the user-facing documentation when the release changes installation, compatibility, configuration, or behavior:

- [Install and Configure](../admin/install.md)
- [Upgrade](../admin/upgrade.md)
- [Compatibility Matrix](../admin/compatibility_matrix.md)
- [Release Notes](../admin/release_notes/index.md)
- [Publishing to PyPI](publishing.md)

Build the documentation before publishing:

```shell
poetry run mkdocs build --no-directory-urls --strict
```

### Verify package build

Build and validate the source distribution and wheel:

```shell
poetry run mkdocs build --no-directory-urls --strict
rm -rf dist
poetry run python -m build
poetry run python -m twine check dist/*
```

The wheel must include the Nautobot app package, migrations, templates, generated static documentation, and app configuration schema.

### Verify tests

Run the project checks in an environment with the required database services:

```shell
INVOKE_NAUTOBOT_FUNCTION_CODES_LOCAL=True poetry run invoke ruff --action lint
INVOKE_NAUTOBOT_FUNCTION_CODES_LOCAL=True poetry run invoke unittest
```

CI also builds and checks the package on every push and pull request.

## Version and Release Notes

Update the version using Poetry:

```shell
poetry version patch
```

Use `minor` or `major` instead of `patch` when the release scope requires it.

Generate or update release notes:

```shell
poetry run invoke generate-release-notes
```

For a new major or minor release, update the `Release Overview` section in the generated file under `docs/admin/release_notes/`.

Commit the release changes:

```shell
git add pyproject.toml poetry.lock CHANGELOG.md mkdocs.yml docs/
git commit -m "Prepare release vX.Y.Z"
```

## Publish to PyPI

Publishing is tag-driven. The `Release` GitHub Actions workflow runs only when a tag matching `v*` is pushed.

Create and push a tag that exactly matches the version in `pyproject.toml`:

```shell
git tag vX.Y.Z
git push origin vX.Y.Z
```

The workflow will:

- check that `vX.Y.Z` matches `project.version`
- build the static documentation used by Nautobot's docs view
- build the package with `python -m build`
- verify the package with `twine check`
- publish to PyPI through Trusted Publishing or `PYPI_API_TOKEN`

If the workflow fails before uploading, fix the issue, delete the failed tag locally and remotely, and push a corrected tag only after the release commit is fixed.

## Post-release Checks

After the workflow finishes:

1. Confirm the package is visible on PyPI.
2. Confirm the published version installs cleanly in a fresh environment.
3. Confirm the GitHub Actions release run used the expected authentication path.
4. Confirm Read the Docs built the tagged documentation.
5. Create any required post-release branch or pull request back into `develop`.

For PyPI project setup and authentication details, see [Publishing to PyPI](publishing.md).
