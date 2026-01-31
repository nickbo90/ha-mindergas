from homeassistant import config_entries
from homeassistant.helpers import selector
import voluptuous as vol
from .const import CONF_API_TOKEN, CONF_SENSOR, CONF_TIME

class MindergasOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        data = self.config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_API_TOKEN, 
                    default=options.get(CONF_API_TOKEN, data.get(CONF_API_TOKEN))
                ): str,
                vol.Required(
                    CONF_SENSOR, 
                    default=options.get(CONF_SENSOR, data.get(CONF_SENSOR))
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="gas")
                ),
                vol.Required(
                    CONF_TIME, 
                    default=options.get(CONF_TIME, data.get(CONF_TIME, "00:00:00"))
                ): selector.TimeSelector()
            })
        )