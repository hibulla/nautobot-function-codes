"""App declaration for nautobot_function_codes."""

from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class NautobotFunctionCodesConfig(NautobotAppConfig):
    """App configuration for the nautobot_function_codes app."""

    name = "nautobot_function_codes"
    verbose_name = "Function Codes"
    version = __version__
    author = "Bartek"
    author_email = "dev@example.com"
    description = "A Nautobot plugin for managing reusable Function Codes."
    base_url = "function-codes"
    min_version = "3.1.0"
    max_version = "4.0.0"
    required_settings = []
    default_settings = {}
    docs_view_name = "plugins:nautobot_function_codes:docs"
    searchable_models = ["functioncode"]
    override_views = "views.override_views"


config = NautobotFunctionCodesConfig
