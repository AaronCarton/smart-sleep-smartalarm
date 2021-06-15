import sys, requests, pygame, socketio # pip install "python-socketio[client]"
sys.path.append(r"/home/student/project-one/Code/Backend") # fix for local relative imports
from repository.DataRepository import DataRepository
from classes import SPIclass, mq, LCDshiftRegister
from subprocess import check_output
from datetime import datetime
from RPi import GPIO

# temp sensor variables
sensor_name = '28-012035c48c15'
TEMP_FILE = f'/sys/bus/w1/devices/{sensor_name}/w1_slave'

# pin variables
CH_LIGHT = 0
CH_SOUND = 2
CH_AIR = 1
CH_R = 22
CH_G = 27
CH_B = 17

# button variables
BTN_LIGHT = 26
BTN_ALARM = 19
BTN_PREV = 13
BTN_NEXT = 6

# classes variables
lcd = LCDshiftRegister.LCD_ShiftRegister()
spi = SPIclass.SpiClass()
sio = socketio.Client()
mq = mq.MQ(CH_AIR)

# other variables
API_URL = 'http://localhost:5000/data'
alarmSound = None
rgbState = True
lcd_state = 0
seconds = 0
alarms = []
light = 0
sound = 0
temp = 0
air = 0


def getWlan0IP():
    output = str(check_output(['ifconfig', 'wlan0']))
    return output.partition('inet')[2].partition('netmask')[0].strip()

def getEth0IP():
    output = str(check_output(['ifconfig', 'eth0']))
    return output.partition('inet')[2].partition('netmask')[0].strip()

def get_temp():
    sensor_file = open(TEMP_FILE, 'r')
    temp = 0
    for line in sensor_file:
        temp = line[line.find('t=')+2:]
    sensor_file.close()
    return int(temp)/1000

def get_air():
    return mq.MQPercentage()['CO']

def get_light():
    # min: 1023
    # max: 80
    value = spi.read_channel(CH_LIGHT)
    return round(abs(((((value - 80) * (100 - 0)) / (1023 - 80))) - 100))

def get_sound():
    return spi.read_channel(CH_SOUND)

def setColor(r, g, b):
    pwmR.ChangeDutyCycle((r/255)*100)
    pwmG.ChangeDutyCycle((g/255)*100)
    pwmB.ChangeDutyCycle((b/255)*100)

def setup():
    # gpio setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup((BTN_LIGHT, BTN_ALARM, BTN_PREV, BTN_NEXT), GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup((CH_R, CH_G, CH_B), GPIO.OUT)
    global pwmR, pwmG, pwmB
    pwmR = GPIO.PWM(CH_R, 2000)
    pwmG = GPIO.PWM(CH_G, 2000)
    pwmB = GPIO.PWM(CH_B, 2000)
    pwmR.start(0)
    pwmG.start(0)
    pwmB.start(0)

    GPIO.add_event_detect(BTN_LIGHT, GPIO.RISING, callback=btn_light, bouncetime=150)
    GPIO.add_event_detect(BTN_ALARM, GPIO.RISING, callback=btn_alarm, bouncetime=150)
    GPIO.add_event_detect(BTN_PREV, GPIO.RISING, callback=btn_prev, bouncetime=150)
    GPIO.add_event_detect(BTN_NEXT, GPIO.RISING, callback=btn_next, bouncetime=150)
    pygame.init()
    # sio setup
    sio.connect('http://localhost:5000')
    sio.start_background_task(read_sensors) # start sensor reading loop in background
    sio.start_background_task(lcd_task)
    sio.start_background_task(alarm_task)
    sio.wait()


### SOCKET IO EVENTS ###
@sio.event
def connect():
    print('connection established')

@sio.event
def RGB_update(data):
    print('new RGB settings recieved:', data)
    global ledR, ledG, ledB
    ledR = int(data['r'])
    ledG = int(data['g'])
    ledB = int(data['b'])
    if rgbState:
        setColor(ledR, ledG, ledB)

@sio.event
def B2F_added_alarm(data):
    # get new alarm from database and add to array
    id = int(data.get('id'))
    new_alarm =  DataRepository.get_alarm_by_id(id)
    alarms.append(new_alarm)
    print(f'adding alarm with ID {id} to list of alarms')
@sio.event
def B2F_deleted_alarm(data):
    # delete alarm from array
    id = int(data.get('id'))
    for alarm in alarms:
        if alarms.get('id') == id:
            alarms.remove(alarm)
            print(f'remove alarm with ID {id} from list of alarms')
            break

    

### BUTTON CALLBACKS ###
def btn_light(ch):
    # toggle rgb state
    global rgbState
    rgbState = not rgbState

    if rgbState: setColor(ledR, ledG, ledB)
    else: setColor(0, 0, 0)

def btn_alarm(ch):
    if pygame.mixer.Channel(0).get_busy():
        alarmSound.stop()

def btn_prev(ch):
    global lcd_state
    if lcd_state == 0:
       lcd_state = 6
    else:
        lcd_state -= 1

def btn_next(ch):
    global lcd_state
    if lcd_state == 6:
       lcd_state = 0
    else:
        lcd_state += 1

### ALARM TASK ###
def alarm_task():
    global alarms, alarmSound

    # alarm task init
    print('\n******* Loading alarms... *******')
    for alarm in DataRepository.get_all_alarms():
        if datetime.now() > alarm.get('enddate'): # clean expired alarms from database
            print('alarm expired, deleting alarm...')
            DataRepository.delete_alarm(alarm.get('id'))
        else:
            alarms.append(alarm)
    print('Loaded alarms: ', alarms)
    # alarm task loop
    print('\n******* Alarms loaded, starting alarm loop... *******')
    while True:
        # loop through all alarms every .5 seconds, if alarm expires, play alarm sound
        currentTime = datetime.now()
        for alarm in alarms:
            if currentTime >= alarm.get('enddate'):
                # play alarm and turn on light
                print('playing alarm...')
                alarmSound = pygame.mixer.Sound("alarm_sound_morning_glory.wav")
                alarmSound.play()
                setColor(ledR, ledG, ledB)
                # delete alarm from database and list
                DataRepository.delete_alarm(alarm.get('id'))
                alarms.remove(alarm)
        sio.sleep(0.5)
        

### LCD TASK ###
def lcd_task():
    print('\n******* Starting LCD screen... *******')
    lcd.init_LCD()
    while True:
        lcd.send_instruction(0x01) # clear current display
        if lcd_state == 0:
            lcd.send_message(datetime.now().strftime('%a %d %B %Y'))
            lcd.send_instruction(0x80|0x40)
            lcd.send_message(datetime.now().strftime('%H:%M:%S'))
        if lcd_state == 1:
            lcd.send_message('Temperature:')
            lcd.send_instruction(0x80|0x40)
            lcd.send_message(f'{round(temp, 1)}C')
        if lcd_state == 2:
            lcd.send_message('Light:')
            lcd.send_instruction(0x80|0x40)
            lcd.send_message(f'{light}%')
        if lcd_state == 3:
            lcd.send_message('Noise:')
            lcd.send_instruction(0x80|0x40)
            lcd.send_message(f'{sound}dB')
        if lcd_state == 4:
            lcd.send_message('C0 level:')
            lcd.send_instruction(0x80|0x40)
            lcd.send_message(f'{round(air, 3)}ppm')
        if lcd_state == 5:
            lcd.send_message('Eth0:')
            lcd.send_instruction(0x80|0x40)
            lcd.send_message(getEth0IP() or 'not found')
        if lcd_state == 6:
            lcd.send_message('Wlan0:')
            lcd.send_instruction(0x80|0x40)
            lcd.send_message(getWlan0IP() or 'not found')
        sio.sleep(0.5)

### READ SENSOR TASK ###
def read_sensors():
    sio.sleep(3)
    global seconds, temp, light, sound, air

    print('\n******* Starting sensor reading... *******')
    while True:
        print('\n************** READINGS **************')
        temp = get_temp()
        light = get_light()
        sound = get_sound()
        air = get_air()
        
        print(f'temp: {temp}')
        print(f'light: {light}')
        print(f'sound: {sound}')
        print(f'air: {air}')

        # send data to web interface
        sio.emit('B2F_latest_data', {'data': {'temp':temp,'light':light,'sound':sound, 'airquality': air}})
        
        # after 10 minutes, save to database
        if (seconds >= 600):
            print('adding to database...')
            requests.post(API_URL, data={'temp':temp,'light':light,'sound':sound, 'airquality': air})
            print('added, waiting 10 minutes...')
            seconds = 0
        sio.sleep(0.5)
        seconds += 2


try:
    setup() # setup, init socketio, start application
    

except KeyboardInterrupt as e:
    pass
finally:
    print('script stopt')
    GPIO.cleanup()