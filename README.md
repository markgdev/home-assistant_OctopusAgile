# home-assistant_OctopusAgile
Octopus Agile custom component for Home Assistant

## Referral code
Feel free to use my referral code and get £50 credit to your account (as well as mine): https://share.octopus.energy/lilac-bison-793

or

<a href="https://www.buymeacoffee.com/markgdev" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

## Installation
Clone this repo and copy custom_components/OctopusAgile to <homeassistant config>/custom_components/OctopusAgile

Alternatively, install via [HACS](https://hacs.xyz/)

## Configuration
NOTE: the GUI configuration flow is currently not implemented.

See the example configuration.yaml config below

### region_code
This should match the [DNO region code](https://www.energy-stats.uk/dno-region-codes-explained/) as per the Octopus Agile API - look for "E-1R-AGILE-18-02-21-" on your [API dashboard](https://octopus.energy/dashboard/developer/) and the next letter is your region code.

### mpan, serial, and auth
Your MPAN and serial number are listed on your [API dashboard page](https://octopus.energy/dashboard/developer/). "*auth*" is your API key from the same page.

### agilerate
As of July 2022 there are now 3 Agile Tariffs :
  * AGILE-18-02-21 - The unit rate is capped at 35p/kWh (including VAT)
  * AGILE-22-07-22 - The unit rate is capped at 55p/kWh (including VAT)
  * AGILE-22-08-31 - The unit rate is capped at 78p/kWh (including VAT)

default if not set is AGILE-18-02-21

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

octopusagile:
  region_code: "L"
  mpan: 00000000
  serial: 00000000
  auth: abc00000000
  startdate: "2020-05-08"
  # Easily switch between agile and go rates.
  # If you include gorate, it'll override
  # the times for the times specified in gotimes
  gorate: 5
  # You can leave godayrate out to go by
  # Agile rates outside of offpeak period
  godayrate: 16.26
  gotimes:
  - "23:30:00"
  - "00:00:00"
  - "00:30:00"
  - "01:00:00"
  - "01:30:00"
  - "02:00:00"
  - "02:30:00"
  - "03:00:00"
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
    block: true/false (Optional, not that if requirements are set, the block times will be taken from there.)
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
- platform: "octopusagile"

```

## Entities
### octopusagile.rates
All future rates stored in entity attributes

### octopusagile.avg_rate_exc_peak
The average rate from the day update_timers runs at 23:00 to 22:30 the next day, excluding the 16:00 to 18:30 time periods where the peak rate is applied.

### octopusagile.avg_rate_inc_peak
The average rate from the day update_timers runs at 23:00 to 22:30 the next day, including the peak.

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

## Development

This repo uses `pipenv` to manage Python versions and dependencies. To get up and running:

* Install [pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv) if you don't already have it.
* Run `pipenv install` to install any required packages and create the right python environment.
