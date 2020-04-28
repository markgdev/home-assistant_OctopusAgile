"""The mark integration."""
# Example service data:
# timers:
#   - entity_id: "switch.tasmota"
#     numHrs: 5
#     day_from: "today"
#     time_from: "19:00:00"
#     day_to: "tomorrow"
#     time_to: "19:00:00"
#     requirements:
#       - numHrs: 1
#         day_from: "today"
#         time_from: "19:00:00"
#         day_to: "tomorrow"
#         time_to: "06:00:00"
#       - numHrs: 1
#         day_from: "tomorrow"
#         time_from: "10:00:00"
#         day_to: "tomorrow"
#         time_to: "16:00:00"
#   - entity_id: "switch.test"
#     numHrs: 2
#     day_from: "today"
#     time_from: "19:00:00"
#     day_to: "tomorrow"
#     time_to: "19:00:00"
# from homeassistant.config import get_default_config_dir
# import OctopusAgile
from .OctopusAgile.Agile import Agile
from homeassistant.helpers.event import track_point_in_time
import homeassistant.util.dt as dt_util
from datetime import datetime, timedelta, date
import logging
from collections import OrderedDict
import json


DOMAIN = "octopusagile"
_LOGGER = logging.getLogger(__name__)
_LOGGER.warning("Starting")
datatorefile = ""

# timerstorefile = f"{get_default_config_dir()}/{DOMAIN}.timers.json"
# timerstorefile = f"/config/{DOMAIN}.timers.json"

def round_time(t):
    # Rounds to nearest half hour
    minute = 00
    if t.minute//30 == 1:
        minute = 30
    return (t.replace(second=0, microsecond=0, minute=minute, hour=t.hour))

def setup(hass, config):
    first_run = True
    """Set up is called when Home Assistant is loading our component."""
    datatorefile = hass.config.path(f"{DOMAIN}.json")
    if "region_code" not in config["OctopusAgile"]:
        _LOGGER.error("region_code must be set for OctopusAgile")
    else:
        region_code = config["OctopusAgile"]["region_code"]
        myrates = Agile(region_code)
        hass.states.set(f"octopusagile.region_code", region_code)

    # Populate timers on restart
    try:
        with open(datatorefile) as f:
            data = json.load(f)
            hass.states.set(f"octopusagile.timers", "", {"timers": data["timers"]})
            hass.states.set(f"octopusagile.rates", "", data["rates"])
            for entity_id, vals in data["device_times"].items():
                hass.states.set(f"octopusagile.{entity_id}", vals["start_time"], vals["attribs"])
            f.close()
    except IOError:
        print(f"{datatorefile} does not exist")

    def handle_update_timers(call):
        """Handle the service call."""
        timer_list = []
        # timers = call.data.get("timers")
        timers = config["OctopusAgile"]["timers"]
        # _LOGGER.warning(timers)
        # _LOGGER.warning(timers_config)
        # _LOGGER.warning(timers)
        for timer in timers:
            # _LOGGER.warning(timer)
            entity_id = timer["entity_id"]
            numHrs = timer["numHrs"]
            # sensor_name = timer["sensor_name"]
            requirements = []
            requirements = timer.get("requirements", [])
            day_from = timer["day_from"]
            time_from = timer["time_from"]
            day_to = timer["day_to"]
            time_to = timer["time_to"]
            params = timer.get("params", None)
            # name = call.data.get("name")
            # numHrs = call.data.get("numHrs")
            # sensor_name = call.data.get("sensor")
            # requirements = call.data.get("requirements")
            # day_from = call.data.get("day_from")
            # time_from = call.data.get("time_from")
            # day_to = call.data.get("day_to")
            # time_to = call.data.get("time_to")
            # _LOGGER.warning(requirements)

            date_from = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            tomorrow = date.today() + timedelta(days=1)
            today = date.today()
            now = datetime.now()
            date_to = tomorrow.strftime("%Y-%m-%dT19:00:00Z")


            if day_from == "today":
                parsed_date_from = today.strftime(f"%Y-%m-%dT{ time_from }Z")
            elif day_from == "tomorrow":
                parsed_date_from = tomorrow.strftime(f"%Y-%m-%dT{ time_from }Z")

            if day_to == "today":
                parsed_date_to = today.strftime(f"%Y-%m-%dT{ time_to }Z")
            elif day_to == "tomorrow":
                parsed_date_to = tomorrow.strftime(f"%Y-%m-%dT{ time_to }Z")

            
            parsed_requirements = []
            for requirement in requirements:
                parsed_requirement = {}
                parsed_requirement["slots"] = requirement["numHrs"]*2
                if requirement["day_from"] == "today":
                    parsed_requirement["time_from"] = today.strftime(f"%Y-%m-%dT{ requirement['time_from'] }Z")
                elif requirement["day_from"] == "tomorrow":
                    parsed_requirement["time_from"] = tomorrow.strftime(f"%Y-%m-%dT{ requirement['time_from'] }Z")

                if requirement["day_to"] == "today":
                    parsed_requirement["time_to"] = today.strftime(f"%Y-%m-%dT{ requirement['time_to'] }Z")
                elif requirement["day_to"] == "tomorrow":
                    parsed_requirement["time_to"] = tomorrow.strftime(f"%Y-%m-%dT{ requirement['time_to'] }Z")
                    parsed_requirements.append(parsed_requirement)
                # _LOGGER.warning(parsed_requirement)
            
            rates = myrates.get_rates(parsed_date_from, parsed_date_to)
            date_rates = rates["date_rates"]
            required_slots = numHrs*2
            min_rates = myrates.get_min_times(required_slots, date_rates, parsed_requirements)
            entity_min_rates = {}
            for time, rate in min_rates.items():
                entity_min_rates[time] = {"params": params, "rate": rate}
            sorted_mins = dict(OrderedDict(sorted(entity_min_rates.items())))
            timer_list.append({"entity_id": entity_id, "times":sorted_mins})

        # Add any free slots to the timer for each moneymaker device
        new_rates = myrates.get_new_rates()["date_rates"]
        # hass.states.set("octopusagile.rates", "", new_rates)
        # moneymakers = call.data.get("moneymakers")
        moneymakers = config["OctopusAgile"]["moneymakers"]
        # _LOGGER.warning("automation:")
        _LOGGER.warning(moneymakers)
        # _LOGGER.warning("config:")
        # _LOGGER.warning(moneymakers_config)
        free_rates = myrates.get_times_below(new_rates, 0)
        for moneymaker_dict in moneymakers:
            # _LOGGER.warning(moneymaker_dict)
            moneymaker = next(iter(moneymaker_dict.items()))
            entity_id = moneymaker[0]
            params = moneymaker[1]
            # _LOGGER.warning(entity_id)
            # _LOGGER.warning(params)
            # _LOGGER.warning(entity_id)
            # _LOGGER.warning(params)
            entity_free_rates = {}
            for time, rate in free_rates.items():
                entity_free_rates[time] = {"params": params, "rate": rate}
            timer_exists = False
            for timer in timer_list:
                if timer["entity_id"] == entity_id:
                    timer["times"].update(entity_free_rates)
                    timer["times"] = dict(OrderedDict(sorted(timer["times"].items())))
                    timer_exists = True
            if not timer_exists:
                _LOGGER.warning("Timer didn't exist")
                timer_list.append({"entity_id": entity_id, "times":entity_free_rates})


        hass.states.set(f"octopusagile.timers", "", {"timers":timer_list})
        
        jsonstr = json.dumps({"timers":timer_list, "rates":new_rates})
        f = open(datatorefile,"w")
        f.write(jsonstr)
        f.close()

        # hass.states.set("sensor.mark_example_temperature", temp)

    def handle_half_hour_timer(call):
        """Handle the service call."""
        # Update the next days rates
        new_rates = myrates.get_new_rates()["date_rates"]
        hass.states.set("octopusagile.rates", "", new_rates)

        # Get next best time to run devices
        # devices = call.data.get("run_devices")
        devices = config["OctopusAgile"]["run_devices"]
        device_times = {}
        for device in devices:
            # _LOGGER.warning(device)
            run_before = device["run_before"]
            energy_time = device["energy_time"]
            run_time = device["run_time"]
            entity_id = device["entity_id"]
            rounded_time = round_time(datetime.utcnow())
            date_from = datetime.strftime(rounded_time, '%Y-%m-%dT%H:%M:%SZ')
            date_to = datetime.strftime((rounded_time + timedelta(days=1)), f"%Y-%m-%dT{run_before}Z")
            rates = myrates.get_rates(date_from, date_to)["date_rates"]
            best_time = myrates.get_min_time_run(energy_time, rates)
            start_time = next(iter(best_time))
            start_time_obj = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ')
            # _LOGGER.warning(start_time)
            rate = best_time[start_time]
            start_in = (start_time_obj - rounded_time).total_seconds()/3600
            end_in = start_in + run_time
            attribs = {"start_time": start_time, "start_in": start_in, "end_in": end_in, "rate": rate}
            hass.states.set(f"octopusagile.{entity_id}", start_time, attribs)
            device_times[entity_id] = {"start_time": start_time, "attribs": attribs}
            # _LOGGER.warning(f"{start_time} {start_in} {end_in} {rate}")


        timers = hass.states.get("octopusagile.timers").attributes["timers"]

        
        now = datetime.utcnow()
        rounded_time = round_time(now)
        rounded_time_str = rounded_time.strftime(f"%Y-%m-%dT%H:%M:%SZ")
        # _LOGGER.warning(rounded_time_str)
        for timer in timers:
            # _LOGGER.warning(timer)
            entity_id = timer["entity_id"]
            times = timer["times"]
            if rounded_time_str in times.keys():
                _LOGGER.warning(f"It's time to turn {entity_id} on!")
                if entity_id.startswith("climate"):
                    if times[rounded_time_str]["params"] is not None:
                        params = times[rounded_time_str]["params"]
                        temp = params[0]["temp"]
                        _LOGGER.warning(temp)
                        hass.services.call("climate", "set_temperature", {'entity_id': entity_id, "temperature": temp})
                    else:
                        _LOGGER.error(f"{entity_id} does not have any params set, don't know what to do")
                else:
                    hass.services.call('switch', 'turn_on', {'entity_id': entity_id})
            else:
                if entity_id.startswith("climate"):
                    hass.services.call("climate", "set_hvac_mode", {'entity_id': entity_id, "hvac_mode": "auto"})
                else:
                    hass.services.call('switch', 'turn_off', {'entity_id': entity_id})
            # for time in times:
            #     _LOGGER.warning(time)

        try:
            with open(datatorefile) as f:
                data = json.load(f)
                f.close()
        except IOError as e:
            print(f"{datatorefile} does not exist here {e}")
        data["device_times"] = device_times
        jsonstr = json.dumps(data)
        f = open(datatorefile,"w")
        f.write(jsonstr)
        f.close()

    def half_hour_timer(nowtime):
        roundedtime = myrates.round_time(nowtime)
        nexttime = roundedtime + timedelta(minutes=30)
        hass.states.set("octopusagile.half_hour_timer_nextupdate", nexttime.strftime("%Y-%m-%dT%H:%M:%SZ"))
        
        try:
            if first_run is False:
                handle_half_hour_timer(None)
                hass.states.set("octopusagile.half_hour_timer_lastupdate", nowtime.strftime("%Y-%m-%dT%H:%M:%SZ"))
        except Exception as e:
            _LOGGER.error(e)

        # Setup timer to run again in 30
        track_point_in_time(hass, half_hour_timer, nexttime)

    def update_timers(nowtime):
        nexttime = nowtime
        nexttime = nexttime.replace(hour=19, minute = 00, second = 00)
        # _LOGGER.warning(nexttime)
        if nexttime <= nowtime:
            nexttime = nexttime + timedelta(days=1)
            # _LOGGER.warning("Runtime has past, scheduling for tomorrow")
        # _LOGGER.warning(nexttime)

        try:
            if first_run is False:
                # _LOGGER.warning("Calling handle update timers")
                handle_update_timers(None)
                hass.states.set("octopusagile.update_timers_lastupdate", nowtime.strftime("%Y-%m-%dT%H:%M:%SZ"))

        except Exception as e:
            _LOGGER.error(e)
            nexttime = nowtime + timedelta(minutes=30)

        hass.states.set("octopusagile.update_timers_nextupdate", nexttime.strftime("%Y-%m-%dT%H:%M:%SZ"))
        track_point_in_time(hass, update_timers, nexttime)


    hass.services.register(DOMAIN, "update_timers", handle_update_timers)
    hass.services.register(DOMAIN, "half_hour", handle_half_hour_timer)
    update_timers(dt_util.utcnow())
    half_hour_timer(dt_util.utcnow())
    first_run = False
    
    # hass.states.set("datetimee_from", datetime.utcnow())

    # Return boolean to indicate that initialization was successfully.
    return True