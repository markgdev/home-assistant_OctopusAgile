# home-assistant_OctopusAgile
Octopus Agile custom component for Home Assistant

## Referral code
Feel free to use my referral code and get £50 credit to your account (as well as mine): https://share.octopus.energy/lilac-bison-793

## Installation
Clone this repo into <homeassistant config>/custom_components

Rename home-assistant_OctopusAgile to OctopusAgile, Home assistant doesn't seem to like the directory name not matching the component name.

## Configuration
Example configuration.yaml config as below.

### region_code
This should match the region code as per the Octopus Agile API

### moneymakers
The concept of moneymakers is devices that should always turn on if the price drops to 0 or below. 
This can either be a switch or climate device. Note that I have only tested this with my tado thermostat. 
Populate params as per the example for climate.

Moneymakers are added to the octopusagile.timers entity which is then checked at the beginning of each half hour to decide if the device should be on or off.

### timers
Timers are used to turn devices on for a set number of hours each day.
I have been using this to turn my immersion heater on for 5 hours a day at the cheapest half hour periods.
day_from/day_to can be either "today" or "tomorrow", this is in reference to when the timers are updated (currently hardcoded to 1900Z each day)

Moneymakers are added to the octopusagile.timers entity which is then checked at the beginning of each half hour to decide if the device should be on or off.

The concept of requirements is best explained with an example. My water heater should turn on for 5 hours each day, 
however it should run for at least and hour between 1900 and 0600 and at least an hour between 1000 and 1600 to ensure that we always have hot water.

Hopefully the other options are self explanatory. 

### run_devices
This creates a entity detailing the best time period to run a device that needs x number of hours to run.
Taking the dishwasher as an example, it runs for 3.5 hours but most energy is used in the first 2.5 so base the run time on 2.5 hours. I want to run the dishwasher before 0800 each night.
An entity named octopusagile.dishwasher is created in Home assistant.

### sensor
Create a sensor for each of: current rate, previous rate and next rate



```yaml

OctopusAgile:
  region_code: "L"
  mpan: 00000000
  serial: 00000000
  auth: abc00000000
  startdate: "2020-05-08"
  moneymakers:
  - switch.water_heater: null
  - climate.downstairs: 
      params:
        temp: 25
  timers:
  - day_from: today
    day_to: tomorrow
    entity_id: switch.water_heater
    numHrs: 5
    params: null
    requirements:
      - day_from: today
        day_to: tomorrow
        numHrs: 1
        time_from: '19:00:00'
        time_to: '06:00:00'
      - day_from: tomorrow
        day_to: tomorrow
        numHrs: 1
        time_from: '10:00:00'
        time_to: '16:00:00'
    time_from: '19:00:00'
    time_to: '19:00:00'

  run_devices:
  - energy_time: 2.5
    entity_id: dishwasher
    run_before: '08:00:00'
    run_time: 3.5
  - energy_time: 2.5
    entity_id: washer
    run_before: '08:00:00'
    run_time: 2.5
  - energy_time: 5
    entity_id: wash_dry
    run_before: '08:00:00'
    run_time: 5
  - energy_time: 2.5
    entity_id: dry
    run_before: '08:00:00'
    run_time: 2.5

sensor:
- platform: "OctopusAgile"

```

## Entities
### octopusagile.rates
All future rates stored in entity attributes

### octopusagile.timers
All timers as created by the timer configuration listed in entity attribute

### octopusagile.region_code
Region code as set in configuration

### octopusagile.half_hour_timer_nextupdate
When the half hour timer will next run

### octopusagile.half_hour_timer_lastupdate	
When the half hour timer last run

### octopusagile.update_timers_nextupdate
When the update timers timer will next run

### octopusagile.update_timers_lastupdate
When the update timers timer last run

### octopusagile.<run_device_name>
A seperate entity for each configured run_device with the time stored in state and start time, start in, end in and average rate stored in the attributes

## Example usage
### Dashboard
Note that i am using an owl energy monitor for the energy usage stats. I will look at pulling these stats direct from octopus once my agile account is setup
![Image of Dashboard](https://raw.githubusercontent.com/markgdev/home-assistant_OctopusAgile/master/images/dashboard.png)

### Dishwasher
![Image of Dashboard](https://raw.githubusercontent.com/markgdev/home-assistant_OctopusAgile/master/images/dishwasher.png)

### Rates
![Image of Dashboard](https://raw.githubusercontent.com/markgdev/home-assistant_OctopusAgile/master/images/rates.png)

### Rates card
[See here](https://github.com/markgdev/home-assistant_OctopusAgile/tree/master/custom_cards)
![Image of Card](https://raw.githubusercontent.com/markgdev/home-assistant_OctopusAgile/master/custom_cards/agile-rates-card-screenshot.png)
