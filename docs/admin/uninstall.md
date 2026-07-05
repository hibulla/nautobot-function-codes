# Uninstall the App from Nautobot

Here you will find any steps necessary to cleanly remove the App from your Nautobot environment.

## Database Cleanup

Prior to removing the app from the `nautobot_config.py`, run the following command to roll back any migration specific to this app.

```shell
nautobot-server migrate nautobot_function_codes zero
```

This removes Function Code and Device Function Code Assignment records managed by the app. Review backups and export any assignment data you need before rolling migrations back.

## Remove App configuration

Remove the configuration you added in `nautobot_config.py` from `PLUGINS` & `PLUGINS_CONFIG`.

## Uninstall the package

```bash
$ pip3 uninstall nautobot-function-codes
```
