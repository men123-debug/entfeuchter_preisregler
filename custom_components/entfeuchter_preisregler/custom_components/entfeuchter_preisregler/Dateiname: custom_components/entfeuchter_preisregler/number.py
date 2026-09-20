"""Number-Entities für die parametrierbaren Werte."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    DEFAULT_SETPOINT_MIN,
    DEFAULT_SETPOINT_MAX,
    DEFAULT_HYSTERESIS,
    DEFAULT_PRICE_LOW,
    DEFAULT_PRICE_HIGH,
    KEY_SETPOINT_MIN,
    KEY_SETPOINT_MAX,
    KEY_HYSTERESIS,
    KEY_PRICE_LOW,
    KEY_PRICE_HIGH,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entities = [
        ParamNumber(entry, KEY_SETPOINT_MIN, "Sollwert Minimum",
                    DEFAULT_SETPOINT_MIN, 0, 100, "%"),
        ParamNumber(entry, KEY_SETPOINT_MAX, "Sollwert Maximum",
                    DEFAULT_SETPOINT_MAX, 0, 100, "%"),
        ParamNumber(entry, KEY_HYSTERESIS, "Hysterese-Breite",
                    DEFAULT_HYSTERESIS, 0, 20, "%"),
        ParamNumber(entry, KEY_PRICE_LOW, "Preisgrenze günstig",
                    DEFAULT_PRICE_LOW, 0, 1000, "EUR/MWh"),
        ParamNumber(entry, KEY_PRICE_HIGH, "Preisgrenze teuer",
                    DEFAULT_PRICE_HIGH, 0, 1000, "EUR/MWh"),
    ]
    async_add_entities(entities)

    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id]["numbers"] = {
        e.param_key: e for e in entities
    }


class ParamNumber(NumberEntity, RestoreEntity):
    _attr_mode = NumberMode.BOX
    _attr_has_entity_name = True

    def __init__(self, entry, param_key, name, default, minimum, maximum, unit):
        self.param_key = param_key
        self._attr_name = name
        self._attr_native_value = default
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"{entry.entry_id}_{param_key}"
        self._attr_device_info = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            try:
                self._attr_native_value = float(last_state.state)
            except (ValueError, TypeError):
                pass

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()
