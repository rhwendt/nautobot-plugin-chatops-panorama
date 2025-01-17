#########################
#                       #
#   Required settings   #
#                       #
#########################

import os
import sys

from django.core.exceptions import ImproperlyConfigured
from nautobot.core.settings import *  # noqa F401,F403 pylint: disable=wildcard-import,unused-wildcard-import
from nautobot.core.settings_funcs import is_truthy, parse_redis_connection

# Enforce required configuration parameters
for key in [
    "NAUTOBOT_ALLOWED_HOSTS",
    "NAUTOBOT_DB_USER",
    "NAUTOBOT_DB_PASSWORD",
    "NAUTOBOT_REDIS_HOST",
    "NAUTOBOT_REDIS_PASSWORD",
    "NAUTOBOT_SECRET_KEY",
]:
    if not os.environ.get(key):
        raise ImproperlyConfigured(f"Required environment variable {key} is missing.")


TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

# This is a list of valid fully-qualified domain names (FQDNs) for the Nautobot server. Nautobot will not permit write
# access to the server via any other hostnames. The first FQDN in the list will be treated as the preferred name.
#
# Example: ALLOWED_HOSTS = ['nautobot.example.com', 'nautobot.internal.local']
ALLOWED_HOSTS = os.getenv("NAUTOBOT_ALLOWED_HOSTS", "").split(" ")

DATABASES = {
    "default": {
        "NAME": os.getenv("NAUTOBOT_DB_NAME", "nautobot"),  # Database name
        "USER": os.getenv("NAUTOBOT_DB_USER", ""),  # Database username
        "PASSWORD": os.getenv("NAUTOBOT_DB_PASSWORD", ""),  # Database password
        "HOST": os.getenv("NAUTOBOT_DB_HOST", "localhost"),  # Database server
        "PORT": os.getenv("NAUTOBOT_DB_PORT", ""),  # Database port (leave blank for default)
        "CONN_MAX_AGE": int(os.getenv("NAUTOBOT_DB_TIMEOUT", 300)),  # Database timeout
        "ENGINE": os.getenv(
            "NAUTOBOT_DB_ENGINE", "django.db.backends.postgresql"
        ),  # Database driver ("mysql" or "postgresql")
    }
}

# Ensure proper Unicode handling for MySQL
#
if DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
    DATABASES["default"]["OPTIONS"] = {"charset": "utf8mb4"}

# duplicate queues setting from RQ for Celery
CELERY_QUEUES = {
    "default": {
        "USE_REDIS_CACHE": "default",
        "DEFAULT_TIMEOUT": 3600,
    },
    "check_releases": {
        "USE_REDIS_CACHE": "default",
    },
    "custom_fields": {
        "USE_REDIS_CACHE": "default",
    },
    "webhooks": {
        "USE_REDIS_CACHE": "default",
    },
}

# The django-redis cache is used to establish concurrent locks using Redis. The
# django-rq settings will use the same instance/database by default.

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": parse_redis_connection(redis_database=0),
        "TIMEOUT": 300,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": os.getenv("NAUTOBOT_REDIS_PASSWORD", ""),
        },
    }
}

# Redis connection to use for caching.

CACHEOPS_REDIS = os.getenv("NAUTOBOT_CACHEOPS_REDIS", parse_redis_connection(redis_database=1))

# Celery broker URL used to tell workers where queues are located

CELERY_BROKER_URL = os.getenv("NAUTOBOT_CELERY_BROKER_URL", parse_redis_connection(redis_database=0))

# Celery results backend URL to tell workers where to publish task results

CELERY_RESULT_BACKEND = os.getenv("NAUTOBOT_CELERY_RESULT_BACKEND", parse_redis_connection(redis_database=0))

# This key is used for secure generation of random numbers and strings. It must never be exposed outside of this file.
# For optimal security, SECRET_KEY should be at least 50 characters in length and contain a mix of letters, numbers, and
# symbols. Nautobot will not run without this defined. For more information, see
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = os.getenv("NAUTOBOT_SECRET_KEY")


#########################
#                       #
#   Optional settings   #
#                       #
#########################

# Specify one or more name and email address tuples representing Nautobot administrators. These people will be notified of
# application errors (assuming correct email settings are provided).
ADMINS = [
    # ['John Doe', 'jdoe@example.com'],
]

# URL schemes that are allowed within links in Nautobot
ALLOWED_URL_SCHEMES = (
    "file",
    "ftp",
    "ftps",
    "http",
    "https",
    "irc",
    "mailto",
    "sftp",
    "ssh",
    "tel",
    "telnet",
    "tftp",
    "vnc",
    "xmpp",
)

# Optionally display a persistent banner at the top and/or bottom of every page. HTML is allowed. To display the same
# content in both banners, define BANNER_TOP and set BANNER_BOTTOM = BANNER_TOP.
BANNER_TOP = os.getenv("NAUTOBOT_BANNER_TOP", "")
BANNER_BOTTOM = os.getenv("NAUTOBOT_BANNER_BOTTOM", "")

# Text to include on the login page above the login form. HTML is allowed.
BANNER_LOGIN = os.getenv("NAUTOBOT_BANNER_LOGIN", "")

# Cache timeout in seconds. Cannot be 0. Defaults to 900 (15 minutes). To disable caching, set CACHEOPS_ENABLED to False
CACHEOPS_DEFAULTS = {"timeout": int(os.getenv("NAUTOBOT_CACHEOPS_TIMEOUT", 900))}

# Set to False to disable caching with cacheops. (Default: True)
CACHEOPS_ENABLED = is_truthy(os.getenv("NAUTOBOT_CACHEOPS_ENABLED", True))

# Maximum number of days to retain logged changes. Set to 0 to retain changes indefinitely. (Default: 90)
CHANGELOG_RETENTION = int(os.getenv("NAUTOBOT_CHANGELOG_RETENTION", 90))

# If True, all origins will be allowed. Other settings restricting allowed origins will be ignored.
# Defaults to False. Setting this to True can be dangerous, as it allows any website to make
# cross-origin requests to yours. Generally you'll want to restrict the list of allowed origins with
# CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGIN_REGEXES.
CORS_ALLOW_ALL_ORIGINS = is_truthy(os.getenv("NAUTOBOT_CORS_ALLOW_ALL_ORIGINS", False))

# A list of origins that are authorized to make cross-site HTTP requests. Defaults to [].
CORS_ALLOWED_ORIGINS = [
    # 'https://hostname.example.com',
]

# A list of strings representing regexes that match Origins that are authorized to make cross-site
# HTTP requests. Defaults to [].
CORS_ALLOWED_ORIGIN_REGEXES = [
    # r'^(https?://)?(\w+\.)?example\.com$',
]

# FQDNs that are considered trusted origins for secure, cross-domain, requests such as HTTPS POST.
# If running Nautobot under a single domain, you may not need to set this variable;
# if running on multiple domains, you *may* need to set this variable to more or less the same as ALLOWED_HOSTS above.
# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = []

# Set to True to enable server debugging. WARNING: Debugging introduces a substantial performance penalty and may reveal
# sensitive information about your installation. Only enable debugging while performing testing. Never enable debugging
# on a production system.
DEBUG = is_truthy(os.getenv("NAUTOBOT_DEBUG", False))

# Enforcement of unique IP space can be toggled on a per-VRF basis. To enforce unique IP space
# within the global table (all prefixes and IP addresses not assigned to a VRF), set
# ENFORCE_GLOBAL_UNIQUE to True.
ENFORCE_GLOBAL_UNIQUE = is_truthy(os.getenv("NAUTOBOT_ENFORCE_GLOBAL_UNIQUE", False))

# Exempt certain models from the enforcement of view permissions. Models listed here will be viewable by all users and
# by anonymous users. List models in the form `<app>.<model>`. Add '*' to this list to exempt all models.
EXEMPT_VIEW_PERMISSIONS = [
    # 'dcim.site',
    # 'dcim.region',
    # 'ipam.prefix',
]

# Global 3rd-party authentication settings
EXTERNAL_AUTH_DEFAULT_GROUPS = []
EXTERNAL_AUTH_DEFAULT_PERMISSIONS = {}

# If hosting Nautobot in a subdirectory, you must set this value to match the base URL prefix configured in your HTTP server (e.g. `/nautobot/`). When not set, URLs will default to being prefixed by `/`.
FORCE_SCRIPT_NAME = None

# When set to `True`, users with limited permissions will only be able to see items in the UI they have access too.
HIDE_RESTRICTED_UI = is_truthy(os.getenv("NAUTOBOT_HIDE_RESTRICTED_UI", False))

# HTTP proxies Nautobot should use when sending outbound HTTP requests (e.g. for webhooks).
# HTTP_PROXIES = {
#     'http': 'http://10.10.1.10:3128',
#     'https': 'http://10.10.1.10:1080',
# }

# IP addresses recognized as internal to the system. The debugging toolbar will be available only to clients accessing
# Nautobot from an internal IP.
INTERNAL_IPS = ("127.0.0.1", "::1")

# Enable custom logging. Please see the Django documentation for detailed guidance on configuring custom logs:
#   https://docs.djangoproject.com/en/stable/topics/logging/
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "normal": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)-7s %(name)s :\n  %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "verbose": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)-7s %(name)-20s %(filename)-15s %(funcName)30s() :\n  %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "normal_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "normal",
        },
    },
    "loggers": {
        "django": {"handlers": ["normal_console"], "level": "INFO"},
        "nautobot": {
            "handlers": ["normal_console"],
            "level": LOG_LEVEL,
        },
        "rq.worker": {
            "handlers": ["normal_console"],
            "level": LOG_LEVEL,
        },
    },
}

# Setting this to True will display a "maintenance mode" banner at the top of every page.
MAINTENANCE_MODE = is_truthy(os.getenv("NAUTOBOT_MAINTENANCE_MODE", False))

# An API consumer can request an arbitrary number of objects =by appending the "limit" parameter to the URL (e.g.
# "?limit=1000"). This setting defines the maximum limit. Setting it to 0 or None will allow an API consumer to request
# all objects by specifying "?limit=0".
MAX_PAGE_SIZE = int(os.getenv("NAUTOBOT_MAX_PAGE_SIZE", 1000))

# The file path where uploaded media such as image attachments are stored. A trailing slash is not needed. Note that
# the default value of this setting is within the invoking user's home directory
# MEDIA_ROOT = os.path.expanduser('~/.nautobot/media')

# By default uploaded media is stored on the local filesystem. Using Django-storages is also supported. Provide the
# class path of the storage driver in STORAGE_BACKEND and any configuration options in STORAGE_CONFIG. For example:
# STORAGE_BACKEND = 'storages.backends.s3boto3.S3Boto3Storage'
# STORAGE_CONFIG = {
#     'AWS_ACCESS_KEY_ID': 'Key ID',
#     'AWS_SECRET_ACCESS_KEY': 'Secret',
#     'AWS_STORAGE_BUCKET_NAME': 'nautobot',
#     'AWS_S3_REGION_NAME': 'eu-west-1',
# }

# Expose Prometheus monitoring metrics at the HTTP endpoint '/metrics'
METRICS_ENABLED = is_truthy(os.getenv("NAUTOBOT_METRICS_ENABLED", False))

# Credentials that Nautobot will uses to authenticate to devices when connecting via NAPALM.
NAPALM_USERNAME = os.getenv("NAUTOBOT_NAPALM_USERNAME", "")
NAPALM_PASSWORD = os.getenv("NAUTOBOT_NAPALM_PASSWORD", "")

# NAPALM timeout (in seconds). (Default: 30)
NAPALM_TIMEOUT = int(os.getenv("NAUTOBOT_NAPALM_TIMEOUT", 30))

# NAPALM optional arguments (see https://napalm.readthedocs.io/en/latest/support/#optional-arguments). Arguments must
# be provided as a dictionary.
NAPALM_ARGS = {}

# Determine how many objects to display per page within a list. (Default: 50)
PAGINATE_COUNT = int(os.getenv("NAUTOBOT_PAGINATE_COUNT", 50))

# Enable installed plugins. Add the name of each plugin to the list.
PLUGINS = ["nautobot_chatops", "nautobot_plugin_chatops_panorama"]

# Plugins configuration settings. These settings are used by various plugins that the user may have installed.
# Each key in the dictionary is the name of an installed plugin and its value is a dictionary of settings.
PLUGINS_CONFIG = {
    "nautobot_chatops": {
        "enable_slack": os.environ.get("ENABLE_SLACK", False),
        "slack_api_token": os.environ.get("SLACK_API_TOKEN"),
        "slack_signing_secret": os.environ.get("SLACK_SIGNING_SECRET"),
        "slack_slash_command_prefix": os.environ.get("SLACK_SLASH_COMMAND_PREFIX", "/"),
        "enable_webex": os.environ.get("ENABLE_WEBEX", False),
        "webex_token": os.environ.get("WEBEX_TOKEN"),
        "webex_signing_secret": os.environ.get("WEBEX_SIGNING_SECRET"),
        "enable_mattermost": os.environ.get("ENABLE_MATTERMOST", False),
        "mattermost_api_token": os.environ.get("MATTERMOST_API_TOKEN"),
        "mattermost_url": os.environ.get("MATTERMOST_URL"),
        "enable_ms_teams": os.environ.get("ENABLE_MS_TEAMS", False),
        "microsoft_app_id": os.environ.get("MICROSOFT_APP_ID"),
        "microsoft_app_password": os.environ.get("MICROSOFT_APP_PASSWORD"),
    },
    "nautobot_plugin_chatops_panorama": {
        "panorama_host": os.environ.get("PANORAMA_HOST"),
        "panorama_user": os.environ.get("PANORAMA_USER"),
        "panorama_password": os.environ.get("PANORAMA_PASSWORD"),
    },
}

# When determining the primary IP address for a device, IPv6 is preferred over IPv4 by default. Set this to True to
# prefer IPv4 instead.
PREFER_IPV4 = is_truthy(os.getenv("NAUTOBOT_PREFER_IPV4", False))

# Rack elevation size defaults, in pixels. For best results, the ratio of width to height should be roughly 10:1.
RACK_ELEVATION_DEFAULT_UNIT_HEIGHT = int(os.getenv("NAUTOBOT_RACK_ELEVATION_DEFAULT_UNIT_HEIGHT", 22))
RACK_ELEVATION_DEFAULT_UNIT_WIDTH = int(os.getenv("NAUTOBOT_RACK_ELEVATION_DEFAULT_UNIT_WIDTH", 220))

# Remote authentication support
REMOTE_AUTH_ENABLED = False
REMOTE_AUTH_BACKEND = "nautobot.core.authentication.RemoteUserBackend"
REMOTE_AUTH_HEADER = "HTTP_REMOTE_USER"
REMOTE_AUTH_AUTO_CREATE_USER = True
REMOTE_AUTH_DEFAULT_GROUPS = []
REMOTE_AUTH_DEFAULT_PERMISSIONS = {}

# This determines how often the GitHub API is called to check the latest release of Nautobot. Must be at least 1 hour.
RELEASE_CHECK_TIMEOUT = int(os.getenv("NAUTOBOT_RELEASE_CHECK_TIMEOUT", 24 * 3600))

# This repository is used to check whether there is a new release of Nautobot available. Set to None to disable the
# version check or use the URL below to check for release in the official Nautobot repository.
RELEASE_CHECK_URL = os.getenv("NAUTOBOT_RELEASE_CHECK_URL", None)
# RELEASE_CHECK_URL = 'https://api.github.com/repos/nautobot/nautobot/releases'

# The length of time (in seconds) for which a user will remain logged into the web UI before being prompted to
# re-authenticate. (Default: 1209600 [14 days])
SESSION_COOKIE_AGE = int(os.getenv("NAUTOBOT_SESSION_COOKIE_AGE", 1209600))  # 2 weeks, in seconds

# By default, Nautobot will store session data in the database. Alternatively, a file path can be specified here to use
# local file storage instead. (This can be useful for enabling authentication on a standby instance with read-only
# database access.) Note that the user as which Nautobot runs must have read and write permissions to this path.
SESSION_FILE_PATH = os.getenv("NAUTOBOT_SESSION_FILE_PATH", None)

# Configure SSO, for more information see docs/configuration/authentication/sso.md
SOCIAL_AUTH_ENABLED = False

# Configure SSO, for more information see docs/configuration/authentication/sso.md
SOCIAL_AUTH_POSTGRES_JSONFIELD = False

# Time zone (default: UTC)
TIME_ZONE = os.getenv("NAUTOBOT_TIME_ZONE", "UTC")

# Date/time formatting. See the following link for supported formats:
# https://docs.djangoproject.com/en/stable/ref/templates/builtins/#date
DATE_FORMAT = os.getenv("NAUTOBOT_DATE_FORMAT", "N j, Y")
SHORT_DATE_FORMAT = os.getenv("NAUTOBOT_SHORT_DATE_FORMAT", "Y-m-d")
TIME_FORMAT = os.getenv("NAUTOBOT_TIME_FORMAT", "g:i a")
SHORT_TIME_FORMAT = os.getenv("NAUTOBOT_SHORT_TIME_FORMAT", "H:i:s")
DATETIME_FORMAT = os.getenv("NAUTOBOT_DATETIME_FORMAT", "N j, Y g:i a")
SHORT_DATETIME_FORMAT = os.getenv("NAUTOBOT_SHORT_DATETIME_FORMAT", "Y-m-d H:i")

# A list of strings designating all applications that are enabled in this Django installation. Each string should be a dotted Python path to an application configuration class (preferred), or a package containing an application.
# https://nautobot.readthedocs.io/en/latest/configuration/optional-settings/#extra-applications
EXTRA_INSTALLED_APPS = []

# Django Debug Toolbar and Django Extensions
DJANGO_TOOLBAR_ENABLED = is_truthy(os.getenv("NAUTOBOT_DJANGO_TOOLBAR_ENABLED", False))
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"
DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _request: DEBUG and not TESTING}

if DJANGO_TOOLBAR_ENABLED and "debug_toolbar" not in EXTRA_INSTALLED_APPS:
    EXTRA_INSTALLED_APPS.append("debug_toolbar")
if DJANGO_TOOLBAR_ENABLED and "debug_toolbar.middleware.DebugToolbarMiddleware" not in MIDDLEWARE:  # noqa F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa F405
