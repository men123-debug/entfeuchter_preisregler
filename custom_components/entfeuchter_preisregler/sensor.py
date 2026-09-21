from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    sensor = CurrentSetpointSensor(entry)
    async_add_entities([sensor])

    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id]["setpoint_sensor"] = sensor


class CurrentSetpointSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Aktueller Sollwert"
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:water-percent"

    def __init__(self, entry: ConfigEntry) -> None:
        self._attr_unique_id = f"{entry.entry_id}_current_setpoint"
        self._attr_native_value = None

    def update_value(self, value: float) -> None:
        self._attr_native_value = round(value, 1)
        if self.hass is not None:
            self.async_write_ha_state()
