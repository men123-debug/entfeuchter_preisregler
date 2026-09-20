"""Config Flow für den Entfeuchter-Preisregler."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
)

from .const import (
    CONF_HUMIDITY_ENTITY,
    CONF_SWITCH_ENTITY,
    CONF_PRICE_ENTITY,
    DOMAIN,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HUMIDITY_ENTITY): EntitySelector(
            EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_SWITCH_ENTITY): EntitySelector(
            EntitySelectorConfig(domain=["switch", "input_boolean"])
        ),
        vol.Required(CONF_PRICE_ENTITY): EntitySelector(
            EntitySelectorConfig(domain="sensor")
        ),
    }
)


class EntfeuchterPreisreglerConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            title = "Entfeuchter-Preisregler"
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return EntfeuchterPreisreglerOptionsFlow(config_entry)


class EntfeuchterPreisreglerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.data
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HUMIDITY_ENTITY,
                    default=current.get(CONF_HUMIDITY_ENTITY),
                ): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Required(
                    CONF_SWITCH_ENTITY,
                    default=current.get(CONF_SWITCH_ENTITY),
                ): EntitySelector(
                    EntitySelectorConfig(domain=["switch", "input_boolean"])
                ),
                vol.Required(
                    CONF_PRICE_ENTITY,
                    default=current.get(CONF_PRICE_ENTITY),
                ): EntitySelector(EntitySelectorConfig(domain="sensor")),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
