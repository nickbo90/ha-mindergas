import logging
import aiohttp
from datetime import timedelta
# Verander Entity naar SensorEntity en importeer de benodigde klassen
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from .const import URL_LATEST_USAGE, URL_FORECAST, URL_USAGE_PER_DEGREE_DAY, URL_UPLOAD_METER, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=6)

async def async_setup_entry(hass, entry, async_add_entities):
    api_token = entry.data.get("api_token")

    sensors = [
        MindergasSensor(api_token, "usage_contract_year", URL_LATEST_USAGE, entry),
        MindergasSensor(api_token, "prognosis_contract_year", URL_FORECAST, entry),
        MindergasSensor(api_token, "usage_per_degree_day", URL_USAGE_PER_DEGREE_DAY, entry),
    ]

    async_add_entities(sensors, update_before_add=True)

# We erven nu over van SensorEntity i.p.v. Entity
class MindergasSensor(SensorEntity):
    def __init__(self, api_token, sensor_type, url, entry):
        self._api_token = api_token
        self._type = sensor_type
        self._url = url
        self._entry = entry
        self._attr_translation_key = sensor_type 
        self._attr_has_entity_name = True
        self._unique_id = f"mindergas_sensor_{sensor_type}"
        self._state = None
        self._attr_entity_registry_enabled_default = True
        
        # LTS Vereisten:
        self._attr_device_class = SensorDeviceClass.GAS
        self._attr_native_unit_of_measurement = "m³"
        
        # Bepaal de juiste state_class op basis van het type sensor
        if sensor_type in ["usage_contract_year", "prognosis_contract_year"]:
            # Dit zijn oplopende totalen binnen het contractjaar -> LTS TOTAL
            self._attr_state_class = SensorStateClass.TOTAL
        else:
            # Dit is een berekend gemiddelde/meting per graaddag -> LTS MEASUREMENT
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Mindergas.nl",
            "manufacturer": "Mindergas.nl",
            "entry_type": "service",
        }

    @property
    def native_value(self):
        # Bij SensorEntity gebruiken we native_value i.p.v. de 'state' property
        return self._state

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def icon(self):
        return "mdi:fire"

    async def async_update(self):
        headers = {
            "AUTH-TOKEN": self._api_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "API-VERSION": "1.0"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._url, headers=headers, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if self._type in ["usage_contract_year", "prognosis_contract_year"]:
                            # Zorg dat de waarde als een echt getal (float) wordt opgeslagen voor statistieken
                            self._state = float(data.get("total", {}).get("value", 0))
                        else:
                            val = data.get("avg_last_365_days", {}).get("value")
                            raw_val = val if val is not None else data.get("value", 0)
                            self._state = float(raw_val)
                        
                        _LOGGER.info("Mindergas: %s updated to %s", self._type, self._state)
                    else:
                        _LOGGER.error("Mindergas API error %s for %s", resp.status, self._type)
        except Exception as e:
            _LOGGER.error("Error updating %s: %s", self._type, e)

async def upload_meter_reading(api_token, reading):
    import datetime
    headers = {"AUTH-TOKEN": api_token, "Content-Type": "application/json"}
    payload = {"date": datetime.date.today().isoformat(), "reading": float(reading)}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(URL_UPLOAD_METER, headers=headers, json=payload) as resp:
                return resp.status == 201
        except Exception as e:
            _LOGGER.error("Mindergas upload error: %s", e)
            return False