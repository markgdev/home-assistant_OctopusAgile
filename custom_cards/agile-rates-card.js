class AgileRatesCard extends HTMLElement {
    set hass(hass) {
        if (!this.content) {
            const card = document.createElement('ha-card');
            card.header = this.title;
            this.content = document.createElement('div');
            this.content.style.padding = '0 16px 16px';

            const style = document.createElement('style');
            style.textContent = `
            table {
                width: 100%;
                padding: 0px;
                spacing: 0px;
            }
            table.sub_table {
                border-collapse: seperate;
                border-spacing: 0px 2px;
            }
            table.main {
                padding: 0px;
            }
            thead th {
                text-align: left;
                padding: 0px;
            }
            td {
                vertical-align: top;
                padding: 2px;
                spacing: 0px;
            }
            tr.rate_row{
                text-align:center;
                width:80px;
            }
            td.time {
                text-align:center;
                vertical-align: middle;
            }
            td.time_red{
                border-bottom: 1px solid Tomato;
            }
            td.time_orange{
                border-bottom: 1px solid orange;
            }
            td.time_green{
                border-bottom: 1px solid MediumSeaGreen;
            }
            td.time_blue{
                border-bottom: 1px solid #391CD9;
            }
            td.rate {
                color:white;
                text-align:center;
                vertical-align: middle;
                width:80px;

                border-top-right-radius:15px;
                border-bottom-right-radius:15px;
            }
            td.red {
                border: 2px solid Tomato;
                background-color: Tomato;
            }
            td.orange {
                border: 2px solid orange;
                background-color: orange;
            }
            td.green {
                border: 2px solid MediumSeaGreen;
                background-color: MediumSeaGreen;
            }
            td.blue {
                border: 2px solid #391CD9;
                background-color: #391CD9;
            }
            `;
            card.appendChild(style);
            card.appendChild(this.content);
            this.appendChild(card);
        }

        const entityId = this.config.entity;
        const state = hass.states[entityId];
        const attributes = this.reverseObject(state.attributes);
        const stateStr = state ? state.state : 'unavailable';
        var tables = "";
        const rates_list_length = Object.keys(attributes).length;
        const rows_per_col = Math.ceil(rates_list_length / this.cols);
        tables = tables.concat("<td><table class='sub_table'><tbody>");
        var table = ""
        var x = 1;
        const mediumlimit = this.mediumlimit;
        const highlimit = this.highlimit;
        const unitstr = this.unitstr;
        const roundUnits = this.roundUnits
        
        Object.keys(attributes).forEach(function (key) {
            const date_milli = Date.parse(key);
            var date = new Date(date_milli);
            const lang = navigator.language || navigator.languages[0];
            var options = { hour12: false, hour: '2-digit', minute:'2-digit'};
            var time_locale = date.toLocaleTimeString(lang, options);
            var colour = "green";
            if(attributes[key] > highlimit) colour = "red";
            else if(attributes[key] > mediumlimit) colour = "orange";
            else if(attributes[key] <= 0 ) colour = "blue";
            table = table.concat("<tr class='rate_row'><td class='time time_"+colour+"'>" + time_locale + "</td><td class='rate "+colour+"'>" + attributes[key].toFixed(roundUnits) + unitstr + "</td></tr>");
            if (x % rows_per_col == 0) {
                tables = tables.concat(table);
                table = "";
                if (rates_list_length != x) {
                    tables = tables.concat("</tbody></table></td>");
                    tables = tables.concat("<td><table class='sub_table'><tbody>");
                }
            };
            x++;

        });
        tables = tables.concat(table);
        tables = tables.concat("</tbody></table></td>");

        this.content.innerHTML = `
        <table class="main">
            <tr>
                ${tables}
            </tr>
        </table>
        `;
    }


    reverseObject(object) {
        var newObject = {};
        var keys = [];

        for (var key in object) {
            keys.push(key);
        }

        for (var i = keys.length - 1; i >= 0; i--) {
            var value = object[keys[i]];
            newObject[keys[i]] = value;
        }

        return newObject;
    }

    setConfig(config) {
        if (!config.entity) {
            throw new Error('You need to define an entity');
        }


        this.config = config;
        if (!config.cols) {
            this.cols = 1;
        }
        else {
            this.cols = config.cols;
        }

        if (!config.title) {
            this.title = 'Agile Rates';
        }
        else {
            this.title = config.title;
        }

        if (!config.mediumlimit) {
            this.mediumlimit = 10;
        }
        else {
            this.mediumlimit = config.mediumlimit;
        }

        if (!config.highlimit) {
            this.highlimit = 15;
        }
        else {
            this.highlimit = config.highlimit;
        }

        if (!config.roundUnits) {
            this.roundUnits = 2;
        }
        else {
            this.roundUnits = config.roundUnits;
        }

        if(!config.showunits) {
            this.unitstr = "p/kWh";
        }
        else {
            if(config.showunits == "true") this.unitstr = "p/kWh";
            else this.unitstr = "";
        }
    }

    // The height of your card. Home Assistant uses this to automatically
    // distribute all cards over the available columns.
    getCardSize() {
        return 3;
    }
}

customElements.define('agile-rates-card', AgileRatesCard);
