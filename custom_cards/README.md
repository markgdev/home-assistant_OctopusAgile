# home-assistant_OctopusAgile rates card
Octopus Agile custom card to display future rates in Home Assistant

## Installation
1. Download agile-rates-card.js
2. Place file in config/www directory. - Create this directory and restart home assistant if this doesn't exist.
3. Add the resource to lovelace in configuration -> Lovelace dashboards -> Resources 
    * Enable advanced mode and put lovelace into edit mode first
    * Url: /local/agile-rates-card.js
    * Resource Type: Javascript module
4. Add card to dashboard
```
entity: octopusagile.rates
type: 'custom:agile-rates-card'
// The below are optional.
cols: 4
mediumlimit: 9
highlimit: 15
```

This card was created with the help of the [Lovelace attributes card](https://community.home-assistant.io/t/lovelace-attributes-card-entity-row/59122) and the Home assistant custom card guide.