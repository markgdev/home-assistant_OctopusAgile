"""Platform for sensor integration."""
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_point_in_time
import homeassistant.util.dt as dt_util
from datetime import timedelta
from .OctopusAgile.Agile import Agile
import logging
_LOGGER = logging.getLogger(__name__)




def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([PreviousRate(hass)])
    add_entities([CurrentRate(hass)])
    add_entities([NextRate(hass)])
    add_entities([MinRate(hass)])


class PreviousRate(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self.hass = hass
        self.entity_id = "sensor.octopus_agile_previous_rate"
        self._state = None
        # self._hass = hass
        self._attributes = {}
        # if "region_code" not in self.config["OctopusAgile"]:
        #     _LOGGER.error("region_code must be set for OctopusAgile")
        # else:
        region_code = hass.states.get("octopusagile.region_code").state
        self.myrates = Agile(region_code)

        self.timer(dt_util.utcnow())


    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Octopus Agile Previous Rate'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "p/kWh"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attributes

    @property    
    def should_poll(self):
        """Return if polling is required."""
        # Disable polling as we're going to update 
        # with the octopusagile.half_hour service
        return False

    def timer(self, nowtime):
        roundedtime = self.myrates.round_time(nowtime)
        nexttime = roundedtime + timedelta(minutes=30)
        self.schedule_update_ha_state(True)
        # Setup timer to run again in 30
        track_point_in_time(self.hass, self.timer, nexttime)

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # attributes = {}
        # attributes['mac'] = 'some data'
        # attributes['sn'] = 'some other data'
        # # attributes['date_to']
        # self._attributes = attributes
        nowtime = self.myrates.round_time(dt_util.utcnow())
        prevtime = nowtime - timedelta(minutes=30)
        rounded_time_str = prevtime.strftime("%Y-%m-%dT%H:%M:%SZ")
        prev_rate = self.hass.states.get("octopusagile.all_rates").attributes.get(rounded_time_str)
        if prev_rate == None:
            _LOGGER.error("Error updating sensor.octopus_agile_previous_rate, check that octopusagile.all_rates populated")
            self._state = "Unknown"
        else:
            prev_rate = round(prev_rate, 2)
            self._state = prev_rate

class CurrentRate(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._state = None
        # self._hass = hass
        self._attributes = {}
        self.hass = hass
        self.entity_id = "sensor.octopus_agile_current_rate"
        # if "region_code" not in self.config["OctopusAgile"]:
        #     _LOGGER.error("region_code must be set for OctopusAgile")
        # else:
        region_code = hass.states.get("octopusagile.region_code").state
        self.myrates = Agile(region_code)
        self.timer(dt_util.utcnow())

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Octopus Agile Current Rate'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "p/kWh"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attributes

    @property    
    def should_poll(self):
        """Return if polling is required."""
        # Disable polling as we're going to update 
        # with the octopusagile.half_hour service
        return False

    def timer(self, nowtime):
        roundedtime = self.myrates.round_time(nowtime)
        nexttime = roundedtime + timedelta(minutes=30)
        self.schedule_update_ha_state(True)
        # Setup timer to run again in 30
        track_point_in_time(self.hass, self.timer, nexttime)

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # attributes = {}
        # attributes['mac'] = 'some data'
        # attributes['sn'] = 'some other data'
        # # attributes['date_to']
        # self._attributes = attributes
        nowtime = self.myrates.round_time(dt_util.utcnow())
        rounded_time_str = nowtime.strftime("%Y-%m-%dT%H:%M:%SZ")
        current_rate = self.hass.states.get("octopusagile.all_rates").attributes.get(rounded_time_str)
        current_rate = round(current_rate, 2)
        self._state = current_rate

class NextRate(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._state = None
        # self._hass = hass
        self._attributes = {}
        self.hass = hass
        self.entity_id = "sensor.octopus_agile_next_rate"
        # if "region_code" not in self.config["OctopusAgile"]:
        #     _LOGGER.error("region_code must be set for OctopusAgile")
        # else:
        region_code = hass.states.get("octopusagile.region_code").state
        self.myrates = Agile(region_code)
        self.timer(dt_util.utcnow())

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Octopus Agile Next Rate'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "p/kWh"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attributes

    @property    
    def should_poll(self):
        """Return if polling is required."""
        # Disable polling as we're going to update 
        # with the octopusagile.half_hour service
        return False

    def timer(self, nowtime):
        roundedtime = self.myrates.round_time(nowtime)
        nexttime = roundedtime + timedelta(minutes=30)
        self.schedule_update_ha_state(True)
        # Setup timer to run again in 30
        track_point_in_time(self.hass, self.timer, nexttime)

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # attributes = {}
        # attributes['mac'] = 'some data'
        # attributes['sn'] = 'some other data'
        # # attributes['date_to']
        # self._attributes = attributes
        nowtime = self.myrates.round_time(dt_util.utcnow())
        nexttime = nowtime + timedelta(minutes=30)
        rounded_time_str = nexttime.strftime("%Y-%m-%dT%H:%M:%SZ")
        next_rate = self.hass.states.get("octopusagile.all_rates").attributes.get(rounded_time_str)
        next_rate = round(next_rate, 2)
        self._state = next_rate

class MinRate(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._state = None
        # self._hass = hass
        self._attributes = {}
        self.hass = hass
        self.entity_id = "sensor.octopus_agile_min_rate"
        # if "region_code" not in self.config["OctopusAgile"]:
        #     _LOGGER.error("region_code must be set for OctopusAgile")
        # else:
        region_code = hass.states.get("octopusagile.region_code").state
        self.myrates = Agile(region_code)
        self.timer(dt_util.utcnow())

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Octopus Agile Minimum Rate'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "p/kWh"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attributes

    @property    
    def should_poll(self):
        """Return if polling is required."""
        # Disable polling as we're going to update 
        # with the octopusagile.half_hour service
        return False

    def timer(self, nowtime):
        roundedtime = self.myrates.round_time(nowtime)
        nexttime = roundedtime + timedelta(minutes=30)
        self.schedule_update_ha_state(True)
        # Setup timer to run again in 30
        track_point_in_time(self.hass, self.timer, nexttime)

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # attributes = {}
        # attributes['mac'] = 'some data'
        # attributes['sn'] = 'some other data'
        # # attributes['date_to']
        # self._attributes = attributes
        new_rates = self.myrates.get_new_rates()["date_rates"]
        rate_dict = self.myrates.get_min_times(1, new_rates, [])
        rate = round(rate_dict[next(iter(rate_dict))], 2)
        # rate = round(self.myrates.get_next_rate(), 2)
        self._state = rate