# Installing the App in Nautobot

Use this guide to install and enable Nautobot Function Codes in a Nautobot environment.

## Prerequisites

- The app is compatible with Nautobot 3.1.0 and higher.
- Python 3.12 or higher is required.
- Databases supported: PostgreSQL, MySQL

!!! note
    Please check the [dedicated page](compatibility_matrix.md) for a full compatibility matrix and the deprecation policy.

### Access Requirements

The app does not require access to external systems. Users who manage assignments need permissions for `DeviceFunctionCodeAssignment` records and, for CSV imports, permission to view and change the target Nautobot devices.

## Install Guide

!!! note
    Apps can be installed from the [Python Package Index](https://pypi.org/) or locally. See the [Nautobot documentation](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/installation/app-install/) for more details. The pip package name for this app is [`nautobot-function-codes`](https://pypi.org/project/nautobot-function-codes/).

The app is distributed as the `nautobot-function-codes` Python package and is imported by Nautobot as `nautobot_function_codes`.

Install the latest released package from PyPI:

```shell
pip install nautobot-function-codes
```

For production deployments, pin the version that has been validated in your Nautobot environment:

```shell
pip install nautobot-function-codes==0.1.0
```

To ensure Nautobot Function Codes is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the pinned package:

```shell
echo "nautobot-function-codes==0.1.0" >> local_requirements.txt
```

Once installed, the app needs to be enabled in your Nautobot configuration. The following block of code below shows the additional configuration required to be added to your `nautobot_config.py` file:

- Append `"nautobot_function_codes"` to the `PLUGINS` list.
- Append the `"nautobot_function_codes"` dictionary to the `PLUGINS_CONFIG` dictionary and override any defaults.

```python
# In your nautobot_config.py
PLUGINS = ["nautobot_function_codes"]

PLUGINS_CONFIG = {
    "nautobot_function_codes": {
        "debug_logging": False,
    }
}
```

Once the Nautobot configuration is updated, run the Post Upgrade command (`nautobot-server post_upgrade`) to run migrations and clear any cache:

```shell
nautobot-server post_upgrade
```

Verify that Nautobot can see the installed package:

```shell
nautobot-server diagnose_nautobot_function_codes
```

Then restart (if necessary) the Nautobot services which may include:

- Nautobot
- Nautobot Workers
- Nautobot Scheduler

```shell
sudo systemctl restart nautobot nautobot-worker nautobot-scheduler
```

## App Configuration

The app behavior can be controlled with the following list of settings:

| Key | Example | Default | Description |
| --- | ------- | ------- | ----------- |
| `debug_logging` | `True` | `False` | Enables verbose debug logging for assignment helper operations. |
