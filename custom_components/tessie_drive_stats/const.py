"""Constants for the Tessie Drive Stats integration."""

from typing import Final

DOMAIN: Final = "tessie_drive_stats"
NAME: Final = "Tessie Drive Stats"

CONF_ACCESS_TOKEN: Final = "access_token"
CONF_VIN: Final = "vin"
CONF_VEHICLE_NAME: Final = "vehicle_name"
CONF_UPDATE_INTERVAL: Final = "update_interval"
CONF_WEEK_START: Final = "week_start"

DEFAULT_UPDATE_INTERVAL: Final = 5
DEFAULT_WEEK_START: Final = "monday"
MIN_UPDATE_INTERVAL: Final = 1
MAX_UPDATE_INTERVAL: Final = 60

WEEKDAYS: Final = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

TESSIE_BASE_URL: Final = "https://api.tessie.com"
REQUEST_TIMEOUT: Final = 30

FRONTEND_VERSION: Final = "0.6.3b2"
FRONTEND_URL: Final = f"/{DOMAIN}/tessie-drive-stats-card.js"
