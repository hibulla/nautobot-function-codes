"""Debug logging helpers for nautobot_function_codes."""

import logging

from nautobot.apps.config import get_app_settings_or_config

LOGGER = logging.getLogger("nautobot_function_codes")


def is_debug_logging_enabled():
    """Return True when verbose plugin debug logging is enabled."""
    return bool(get_app_settings_or_config("nautobot_function_codes", "debug_logging", fallback=False))


def debug_log(message, *args, **kwargs):
    """Log a debug message when plugin debug logging is enabled."""
    if is_debug_logging_enabled():
        LOGGER.debug(message, *args, **kwargs)
