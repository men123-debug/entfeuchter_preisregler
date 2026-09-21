"""Entfeuchter-Preisregler: Hysterese-Regelung mit preisabhängigem Sollwert."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    DOMAIN,
    CONF_HUMIDITY_ENTITY,
    CONF_SWITCH_ENTITY,
    CONF_PRICE_ENTITY,
    KEY_SETPOINT_MIN,
    KEY_SETPOINT_MAX,
    KEY_HYSTERESIS,
    KEY_PRICE_LOW,
    KEY_PRICE_HIGH,
    DEFAULT_SETPOINT_MIN,
    DEFAULT_SETPOINT_MAX,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["number", "sensor"]


def _float_state(hass: HomeAssistant, entity_id):
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    if state is None or state.state in ("unknown", "unavailable"):
        return None
    try:
        return float(state.state)
    except (ValueError, TypeError):
        return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    humidity_entity = entry.data[CONF_HUMIDITY_ENTITY]
    switch_entity = entry.data[CONF_SWITCH_ENTITY]
    price_entity = entry.data[CONF_PRICE_ENTITY]

    store = hass.data[DOMAIN][entry.entry_id]
    store.setdefault(
        "current_setpoint", (DEFAULT_SETPOINT_MIN + DEFAULT_SETPOINT_MAX) / 2
    )

    def _get_number(key, default):
        numbers = store.get("numbers", {})
        entity = numbers.get(key)
        if entity is not None and entity.native_value is not None:
            return float(entity.native_value)
        return default

    async def _apply_switch(turn_on: bool) -> None:
        domain = switch_entity.split(".")[0]
        service = "turn_on" if turn_on else "turn_off"
        await hass.services.async_call(
            domain, service, {"entity_id": switch_entity}, blocking=False
        )

    async def _evaluate_hysterese(_event=None) -> None:
        humidity = _float_state(hass, humidity_entity)
        if humidity is None:
            return
        hysteresis = _get_number(KEY_HYSTERESIS, 5.0)
        setpoint = store["current_setpoint"]
        upper = setpoint + hysteresis
        lower = setpoint - hysteresis

        if humidity > upper:
            await _apply_switch(True)
        elif humidity < lower:
            await _apply_switch(False)

    async def _evaluate_preis(_event=None) -> None:
        price = _float_state(hass, price_entity)
        if price is None:
            return
        price_low = _get_number(KEY_PRICE_LOW, 140.0)
        price_high = _get_number(KEY_PRICE_HIGH, 190.0)
        setpoint_min = _get_number(KEY_SETPOINT_MIN, DEFAULT_SETPOINT_MIN)
        setpoint_max = _get_number(KEY_SETPOINT_MAX, DEFAULT_SETPOINT_MAX)

        if price < price_low:
            store["current_setpoint"] = setpoint_min
        elif price > price_high:
            store["current_setpoint"] = setpoint_max

        sensor = store.get("setpoint_sensor")
        if sensor is not None:
            sensor.update_value(store["current_setpoint"])

        await _evaluate_hysterese()

    @callback
    def _on_price_change(event):
        hass.async_create_task(_evaluate_preis(event))

    @callback
    def _on_humidity_change(event):
        hass.async_create_task(_evaluate_hysterese(event))

    unsub_price = async_track_state_change_event(
        hass, [price_entity], _on_price_change
    )
    unsub_humidity = async_track_state_change_event(
        hass, [humidity_entity], _on_humidity_change
    )
    store["unsub"] = [unsub_price, unsub_humidity]

    await _evaluate_preis()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    store = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    for unsub in store.get("unsub", []):
        unsub()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
