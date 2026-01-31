from homeassistant import config_entries
from homeassistant.helpers import selector
import voluptuous as vol
from .const import DOMAIN, CONF_API_TOKEN, CONF_SENSOR, CONF_TIME

class MindergasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    @staticmethod
    def async_get_options_flow(config_entry):
        from .options_flow import MindergasOptionsFlowHandler
        return MindergasOptionsFlowHandler()

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Mindergas.nl", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_TOKEN): str,
                vol.Required(CONF_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", device_class="gas")
                ),
                vol.Required(CONF_TIME, default="00:00:00"): selector.TimeSelector()
            })
        )