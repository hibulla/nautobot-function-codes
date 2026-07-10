# Upgrading the App

Here you will find any steps necessary to upgrade the App in your Nautobot environment.

## Upgrade Guide

When a new release is available, update the Python package and run Nautobot's post-upgrade command within the runtime environment of your Nautobot installation.

```shell
pip install --upgrade nautobot-function-codes
nautobot-server post_upgrade
```

Review the release notes before upgrading, especially when moving between minor or major app versions.

For production environments, pin the target version explicitly after reviewing compatibility:

```shell
pip install --upgrade nautobot-function-codes==X.Y.Z
nautobot-server post_upgrade
nautobot-server diagnose_nautobot_function_codes
```

Restart Nautobot services after the upgrade so the new plugin code is loaded.
