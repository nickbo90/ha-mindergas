import logging
from datetime import datetime, timedelta
import asyncio
from homeassistant.helpers.event import async_track_time_change, async_call_later
from .const import DOMAIN, CONF_API_TOKEN, CONF_SENSOR, CONF_TIME

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    api_token = entry.options.get(CONF_API_TOKEN, entry.data.get(CONF_API_TOKEN))
    source_sensor = entry.options.get(CONF_SENSOR, entry.data.get(CONF_SENSOR))
    update_time_str = entry.options.get(CONF_TIME, entry.data.get(CONF_TIME, "00:00:00"))

    try:
        parts = update_time_str.split(":")
        hh = int(parts[0])
        mm = int(parts[1])
        ss = int(parts[2]) if len(parts) > 2 else 0
    except (ValueError, AttributeError):
        _LOGGER.error("Mindergas: Invalid time format '%s', defaulting to 00:00:00", update_time_str)
        hh, mm, ss = 0, 0, 0

    async def scheduled_upload(now):
        _LOGGER.info("Mindergas: Scheduled upload started.")

        state_obj = hass.states.get(source_sensor)
        if not state_obj or state_obj.state in ["unknown", "unavailable"]:
            _LOGGER.warning("Mindergas: Upload skipped, source sensor not available.")
            return

        from .sensor import upload_meter_reading
        success = await upload_meter_reading(api_token, state_obj.state)

        if success:
            _LOGGER.info("Mindergas: Meter reading uploaded successfully.")
            # Schedule refresh 1 minute later using async_call_later
            async def refresh_callback(_):
                _LOGGER.info("Mindergas: Refreshing sensors (1 minutes after upload).")
                mindergas_entities = [
                    entity_id for entity_id in hass.states.async_entity_ids("sensor")
                    if entity_id.startswith("sensor.mindergas_")
                ]
                
                if not mindergas_entities:
                    _LOGGER.warning("Mindergas: No sensor found")
                    return

                tasks = [
                    hass.services.async_call(
                        "homeassistant",
                        "update_entity",
                        {"entity_id": entity_id},
                        blocking=True, 
                    )
                    for entity_id in mindergas_entities
                ]

                await asyncio.gather(*tasks)
            async_call_later(hass, 60, lambda _now: hass.loop.create_task(refresh_callback(_now)))
        else:
            _LOGGER.error("Mindergas: Upload failed.")

    if hass.data.get(DOMAIN, {}).get("upload_unsub"):
        _LOGGER.debug("Mindergas: Removing previous upload cronjob")
        hass.data[DOMAIN]["upload_unsub"]()
        del hass.data[DOMAIN]["upload_unsub"]

    _LOGGER.debug("Mindergas: Registering upload cronjob at %02d:%02d:%02d", hh, mm, ss)
    upload_unsub = async_track_time_change(
        hass,
        scheduled_upload,
        hour=hh,
        minute=mm,
        second=ss,
    )
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["upload_unsub"] = upload_unsub
    entry.async_on_unload(upload_unsub)

    # Reload integration on options update
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def update_listener(hass, entry):
    _LOGGER.debug("Mindergas: Options updated, reloading integration...")
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    if DOMAIN in hass.data and "upload_unsub" in hass.data[DOMAIN]:
        _LOGGER.debug("Mindergas: Removing upload cronjob on unload")
        hass.data[DOMAIN]["upload_unsub"]()
        del hass.data[DOMAIN]["upload_unsub"]
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
