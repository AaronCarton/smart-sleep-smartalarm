const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
/// <reference path="datahandler.js"/>

//#region ***  DOM references ***
let htmlAlarmGrid, chart, today, colorPicker
// selectors
let htmlDropdownReadingSelected, htmlDropdownChartvalueSelected, htmlChartDateSelector
// sleep quality
let hmtlSleepPercentageText, htmlSleepPercentageRadial
//#endregion

//#region ***  Callback-Visualisation - show___ ***
const showLatestData = (data) => {
    console.log('latest readings:', data);
    htmlDropdownReadingSelected.innerHTML = 'Latest'
    document.querySelector('.js-temp').innerHTML = data['temp'] ? data['temp'].toFixed(1) + '°C' : 'not measured'
    document.querySelector('.js-light').innerHTML = data['light'] ? data['light'] + '%' : 'not measured'
    document.querySelector('.js-sound').innerHTML = data['sound'] ? data['sound'] + 'dB' : 'not measured'
    document.querySelector('.js-air').innerHTML = data['airquality'] ? data['airquality'].toFixed(3) + 'ppm' : 'not measured'

    // set sleep percentage
    showSleepPercentage(data);
}

const showAverageData = (data) => {
    htmlDropdownReadingSelected.innerHTML = 'Average'
    document.querySelector('.js-temp').innerHTML = data['avg_temp'] ? Math.round(data['avg_temp']) + '°C' : 'not measured'
    document.querySelector('.js-light').innerHTML = data['avg_light'] ? data['avg_light'] + '%' : 'not measured'
    document.querySelector('.js-sound').innerHTML = data['avg_sound'] ? data['avg_sound'] + 'dB' : 'not measured'
    document.querySelector('.js-air').innerHTML = data['avg_airquality'] ? data['avg_airquality'].toFixed(3) + 'ppm' : 'not measured'
}

const showAlarms = (jsonObject) => {
    let html = ''
    console.info('*************** LOADING ALARMS ***************');
    for (const alarm of jsonObject.data) {
        console.log(alarm);
        let date = new Date(alarm.enddate) // create date from string
        date.setHours(date.getHours() - 2) // account for time zone
        let time = date.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true }) // convert to AM/PM
        html +=
            `<div data-id="${alarm.id}" class="js-alarm c-alarm o-layout o-layout--align-center o-layout--justify-space-between">
            <div class="js-alarm-info o-layout o-layout-column o-layout--align-content-space-around">
                <div class="js-alarm-description c-alarm-description c-lead c-lead--md">${alarm.name}</div>
                <div class="js-alarm-time c-lead c-lead--lg">${time}</div>
            </div>
            <div class="js-alarm-toggle c-toggle o-layout o-layout--align-center ${alarm.active ? '' : 'c-toggle-disabled'}">
                <span class="c-toggle-dot"></span>
            </div>
        </div>`
    }

    htmlAlarmGrid.innerHTML = html
    listenToAlarmToggle() // start toggle listeners
    listenToDeleteAlarm(); // start delete listeners
}

const showChartData = (data) => {
    let labels = [];
    let readings = [];
    for (const item of data.data) {
        labels.push(new Date(item.timestamp).toLocaleString('en-US', { hour: 'numeric', hour12: true }));
        switch (htmlDropdownChartvalueSelected.innerHTML) {
            case 'Temperature':
                readings.push(item.avg_temp);
                break;
            case 'Light':
                readings.push(item.avg_light);
                break;
            case 'Sound':
                readings.push(item.avg_sound);
                break;
            case 'CO level':
                readings.push(item.avg_airquality);
                break;
        }

    }
    drawChart(labels, readings, htmlDropdownChartvalueSelected.innerHTML);
};

const drawChart = (labels, data, type) => {
    console.info('*************** LOADING CHART ***************');
    console.log(`Chart data (${type}, ${htmlChartDateSelector.value})`, data);
    let options = {
        series: [
            {
                name: type,
                data: data,
            },
        ],
        labels: labels,
        noData: {
            text: 'No data recorded',
            offsetY: -15,
            style: {
                color: '#F4F4F6',
                fontSize: '14px',
                fontFamily: undefined
            }
        },
    }
    chart.updateOptions(options);
};

const showOverviewModal = () => {
    console.log('test');
    let temp = parseInt(document.querySelector('.js-temp').innerHTML)
    let light = parseInt(document.querySelector('.js-light').innerHTML)
    let html = ''
    if (temp > 18.5) {
        html += `<div class="c-modal--overview-warning">
        <div class="c-lead c-lead--md">Temperature too high</div>
        <div class="c-lead c-lead--sm">Last measured temperature is ${temp}C, the ideal temperature is 18.5C</div>
    </div>`
    }
    if (light > 5) {
        html += `<div class="c-modal--overview-warning">
        <div class="c-lead c-lead--md">There is too much light</div>
        <div class="c-lead c-lead--sm">Last measured amount of light is ${light}%, the ideal amount of light should be below 5%</div>
    </div>`
    }
    document.querySelector('.c-modal--overview-body').innerHTML = html
}

const showSleepPercentage = (data) => {
    // calculate closeness of values to their ideal values
    let tempValue = calculateCloseness(40, 18.5, data['temp'])
    let lightValue = calculateCloseness(100, 0, data['light'])
    // combine into a total percentage
    let totalValuePerc = Math.round(((tempValue + lightValue) / 2) * 100)
    // display on website
    hmtlSleepPercentageText.innerHTML = `${totalValuePerc}%`
    htmlSleepPercentageRadial.className = htmlSleepPercentageRadial.className.replace(/(p100)|(p0*\d{1,2})/, `p${totalValuePerc}`)

}
//#endregion

//#region ***  Callback-No Visualisation - callback___  ***
//#endregion

//#region ***  Data Access - get___ ***
const getHourlySensorData = () => handleData(`http://${lanIP}/data/${htmlChartDateSelector.value}/average/hourly`, showChartData);;
const getAlarms = () => handleData(`http://${lanIP}/alarms`, showAlarms)
const getLatestData = () => handleData(`http://${lanIP}/data/latest`, showLatestData)
const getAverageData = () => handleData(`http://${lanIP}/data/${today}/average`, showAverageData)
const getRGBdata = () => handleData(`http://${lanIP}/rgb`, initColorPicker)
//#endregion

//#region ***  Event Listeners - listenTo___ ***
const listenToSocket = () => {
    socket.on("connect", function () {
        console.log(`connected to socket webserver`);
    });

    // display new data when read from sensors
    socket.on('B2F_latest_data', (jsonObject) => {
        if (htmlDropdownReadingSelected.innerHTML === 'Latest') showLatestData(jsonObject.data)
    })

    // update toggle status of alarm when changed
    socket.on('B2F_update_alarm_status', (jsonObject) => {
        console.log(`socketio update alarm:`);
        console.log(jsonObject);
        setTimeout(() =>
            updated_alarm = document.querySelectorAll('.js-alarm').forEach(alarm => {
                if (alarm.dataset.id === jsonObject.id) {
                    const toggleElement = alarm.children[1] // get toggle element of alarm
                    jsonObject.active ? toggleElement.classList.remove('c-toggle-disabled') : toggleElement.classList.add('c-toggle-disabled')
                }
            }), 300) // wait 300 milliseconds for toggle to update

    })
}

const listenToDropdownclick = () => {
    // latest & average dropdown
    document.querySelector('.dropdown-reading').addEventListener('click', () => {
        document.querySelectorAll('.dropdown-reading>.dropdown-content').forEach(item => item.classList.toggle("show"))
    })

    // graph value dropdown
    document.querySelector('.dropdown-value').addEventListener('click', () => {
        document.querySelectorAll('.dropdown-value>.dropdown-content').forEach(item => item.classList.toggle("show"))
    })
}

const listenToAlarmToggle = () => {
    document.querySelectorAll('.js-alarm-toggle').forEach(toggle => toggle.addEventListener('click', function () {
        handleData(
            `http://${lanIP}/alarm/${this.parentElement.dataset.id}`,
            () => this.classList.toggle('c-toggle-disabled'),
            null,
            'PUT',
            JSON.stringify({ active: this.classList.contains('c-toggle-disabled') })
        )

    }))
}

const listenToDropdownSelection = () => {
    // latest & average dropdown
    document.querySelector('.js-dropdown-latest').addEventListener('click', getLatestData)
    document.querySelector('.js-dropdown-averages').addEventListener('click', getAverageData)

    // chart date selector
    htmlChartDateSelector.addEventListener('input', getHourlySensorData)

    // chart value dropdown
    document.querySelector('.js-dropdown-temp').addEventListener('click', () => {
        htmlDropdownChartvalueSelected.innerHTML = 'Temperature'
        getHourlySensorData()
    })
    document.querySelector('.js-dropdown-light').addEventListener('click', () => {
        htmlDropdownChartvalueSelected.innerHTML = 'Light'
        getHourlySensorData()
    })
    document.querySelector('.js-dropdown-sound').addEventListener('click', () => {
        htmlDropdownChartvalueSelected.innerHTML = 'Sound'
        getHourlySensorData()
    })
    document.querySelector('.js-dropdown-air').addEventListener('click', () => {
        htmlDropdownChartvalueSelected.innerHTML = 'C0 level'
        getHourlySensorData()
    })
}

const listenToModalButtons = () => {
    // show alarm modal
    document.querySelector('.js-alarm-add').addEventListener('click', () => {
        document.querySelector('.modal--alarm').classList.remove('c-modal--hidden')
        document.querySelectorAll('body').forEach(modal => modal.style.overflow = 'hidden')
    })
    // show overview modal
    document.querySelector('.js-overview-button').addEventListener('click', () => {
        document.querySelector('.modal--overview').classList.remove('c-modal--hidden')
        document.querySelectorAll('body').forEach(modal => modal.style.overflow = 'hidden')
        showOverviewModal();
    })
    // hide modals
    document.querySelectorAll('.c-modal-close, .c-modal-dim').forEach(el => el.addEventListener('click', () => {
        document.querySelectorAll('.js-modal').forEach(modal => modal.classList.add('c-modal--hidden'))
        document.querySelectorAll('body').forEach(modal => modal.style.overflow = 'auto')
    }))
}

const listenToColorPickerButton = () => {
    document.querySelector('.js-color-button').addEventListener('click', () => {
        let hex = document.querySelector('.js-hex').value
        let rgb = document.querySelector('.js-rgb').value.split(',')
        console.log(hex);
        console.log(rgb);
        handleData(`http://${lanIP}/rgb`,
            () => {
                console.log('Saved new color!', hex, rgb)
                socket.emit('RGB_update', { r: rgb[0], g: rgb[1], b: rgb[2] })
            },
            null,
            'PUT',
            JSON.stringify({ r: rgb[0], g: rgb[1], b: rgb[2], hex: hex }))
    })
}

const listenToAddAlarmButton = () => {
    document.querySelector('.js-add-alarm-button').addEventListener('click', () => {
        // if 6 or more alarms already set, don't set
        if (htmlAlarmGrid.childElementCount >= 6) {
            htmlTime.setCustomValidity("Max amount of set alarms reached!")
            htmlTime.reportValidity()
        }
        else {
            let htmlName = document.querySelector('.js-add-alarm-name')
            let htmlTime = document.querySelector('.js-add-alarm-time')
            let alarmTime = new Date(new Date().toDateString() + " " + htmlTime.value)
            if (new Date() > alarmTime) {
                htmlTime.setCustomValidity("Cannot set alarm in the past")
                htmlTime.reportValidity()
            } else {
                // convert JS date to MySQL date
                let convertedTime = alarmTime.toISOString().split('T')[0] + ' ' + alarmTime.toTimeString().split(' ')[0]
                handleData(`http://${lanIP}/alarms`, () => console.log(`Alarm '${htmlName.value} set for '`, alarmTime), null, 'POST', JSON.stringify({
                    name: htmlName.value, date: convertedTime
                }))
                htmlTime.setCustomValidity("Alarm set")
                htmlTime.reportValidity()
                getAlarms(); // reload alarms
                // close modal
                document.querySelector('.modal--alarm').classList.add('c-modal--hidden')
            }
        }
    })
}

const listenToDeleteAlarm = () => {
    document.querySelectorAll('.js-alarm').forEach(alarm => alarm.addEventListener('click', function () {
        // add alarm ID to confirmation button
        const idAlarm = this.dataset.id
        document.querySelector('.js-remove-alarm-confirm').dataset.id = idAlarm

        // open confirmation modal
        document.querySelector('.modal--confirmation').classList.remove('c-modal--hidden')
        document.querySelectorAll('body').forEach(modal => modal.style.overflow = 'hidden')
    }))
    listenToDeleteConfirmation() // listen to click on 'Yes' button
}

const listenToDeleteConfirmation = () => {
    // confirm button
    document.querySelector('.js-remove-alarm-confirm').addEventListener('click', function () {
        const idAlarm = this.dataset.id
        handleData(`http://${lanIP}/alarm/${idAlarm}`, (json) => {
            // close modal
            document.querySelectorAll('.js-modal').forEach(modal => modal.classList.add('c-modal--hidden'))
            document.querySelectorAll('body').forEach(modal => modal.style.overflow = 'auto')
            // reload alarms
            getAlarms();
        }, null, 'DELETE', null)
    })
    // deny button
    document.querySelector('.js-remove-alarm-deny').addEventListener('click', function () {
        // close modal
        document.querySelectorAll('.js-modal').forEach(modal => modal.classList.add('c-modal--hidden'))
        document.querySelectorAll('body').forEach(modal => modal.style.overflow = 'auto')
        // set ID back to 0
        document.querySelector('.js-remove-alarm-confirm').dataset.id = 0
    })

}
//#endregion

//#region ***  INIT / DOMContentLoaded  ***
const initChart = () => {
    let options = {
        chart: {
            id: 'readingChart',
            type: 'line',
            foreColor: '#F4F4F6',
            height: '240px',
            width: '717px',
            offsetY: 20,
            toolbar: {
                show: false,
            },
        },
        stroke: {
            curve: 'smooth',
        },
        tooltip: {
            theme: false,

        },
        xaxis: {
            tooltip: {
                enabled: false
            },
            labels: {
                style: {
                    fontSize: '10px',
                },
            },
        },
        dataLabels: {
            enabled: false,
        },
        series: [
            {
                name: '...',
                data: [],
            },
        ],
        labels: [],
        noData: {
            text: 'loading...',
            offsetY: -15,
            style: {
                color: '#F4F4F6',
                fontSize: '14px',
                fontFamily: undefined
            }
        },
        colors: ['#FE1C78', '#403773', '#403773'],
        grid: {
            borderColor: "#403773",
        },
        responsive: [{
            breakpoint: 720,
            options: {
                chart: {
                    width: '330px',
                },
            }
        },
        {
            breakpoint: 376,
            options: {
                chart: {
                    width: '285px',
                },
            }
        }
            ,
        {
            breakpoint: 321,
            options: {
                chart: {
                    width: '230px',
                },
            }
        }]
    }
    chart = new ApexCharts(document.querySelector('.js-chart'), options);
    chart.render();
}

const initColorPicker = (jsonObject) => {
    console.info('*************** LOADING COLOR WHEEL ***************');
    // init color wheel
    colorPicker = new iro.ColorPicker('#picker', {
        width: 250,
        color: jsonObject.data.hex
    });

    // listen to color wheel change, change inputs accordingly
    colorPicker.on(['color:init', 'color:change'], function (color) {
        document.querySelector('.js-hex').value = color.hexString
        document.querySelector('.js-rgb').value = `${color.rgb['r']},${color.rgb['g']},${color.rgb['b']}`

    });
    // listen to input change, change color wheel accordingly
    document.querySelector('.js-hex').addEventListener('input', function () {
        colorPicker.color.hexString = this.value
    })
    document.querySelector('.js-rgb').addEventListener('input', function () {
        arrRGB = this.value.split(',')
        colorPicker.color.rgb = { r: arrRGB[0], g: arrRGB[1], b: arrRGB[2] }
    })
}

const init = () => {
    console.info('init');
    initChart() // create empty chart
    getRGBdata(); // get rgb data and create color wheel

    // get DOM elements
    htmlAlarmGrid = document.querySelector('.js-alarm-grid')

    htmlDropdownReadingSelected = document.querySelector('.js-dropdown-selected')
    htmlDropdownChartvalueSelected = document.querySelector('.js-dropdown-value-selected')
    htmlChartDateSelector = document.querySelector('.js-chart-date')

    hmtlSleepPercentageText = document.querySelector('.js-sleep-percentage')
    htmlSleepPercentageRadial = document.querySelector('.js-sleep-radial')

    today = new Date().toISOString().slice(0, 10)
    console.info('current date:', today);
    htmlChartDateSelector.value = today // set date input to today

    // get data
    getHourlySensorData();
    getAlarms();

    // create listeners
    listenToDropdownclick();
    listenToDropdownSelection();
    listenToModalButtons();
    listenToColorPickerButton();
    listenToAddAlarmButton();

    // listen to socket events
    listenToSocket();
}
//#endregion

document.addEventListener('DOMContentLoaded', init)



// closeness calculation
// for example: max: 10
// ideal: 5, x: 4 => 80%
// ideal: 5, x: 6 => 80%
// ideal: 5, x: 5 => 100%
const calculateCloseness = function (max, ideal, x) {
    return Math.abs((max - ideal) - Math.abs(ideal - x)) / (max - ideal)
}