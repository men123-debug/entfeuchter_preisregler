"""Konstanten für die Entfeuchter-Preisregler-Integration."""

DOMAIN = "entfeuchter_preisregler"

CONF_HUMIDITY_ENTITY = "humidity_entity"
CONF_SWITCH_ENTITY = "switch_entity"
CONF_PRICE_ENTITY = "price_entity"

DEFAULT_SETPOINT_MIN = 55.0
DEFAULT_SETPOINT_MAX = 65.0
DEFAULT_HYSTERESIS = 5.0
DEFAULT_PRICE_LOW = 140.0
DEFAULT_PRICE_HIGH = 190.0
DEFAULT_DRY_RATE_THRESHOLD = -3.0

KEY_SETPOINT_MIN = "setpoint_min"
KEY_SETPOINT_MAX = "setpoint_max"
KEY_HYSTERESIS = "hysteresis"
KEY_PRICE_LOW = "price_low"
KEY_PRICE_HIGH = "price_high"
KEY_DRY_RATE_THRESHOLD = "dry_rate_threshold"
