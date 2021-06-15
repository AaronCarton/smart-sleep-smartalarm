from RPi import GPIO
import time

class LCDclass():
    global DELAY
    DELAY = 0.00001
    def __init__(self, datapins=[16,12,25,24,23,26,19,13], enablepin=20, registerselectpin=21):
        self.datapins = datapins
        self.ENABLE = enablepin
        self.RS = registerselectpin
        self.last_sent_message = ''
        GPIO.setmode(GPIO.BCM)
        GPIO.setup((self.ENABLE, self.RS),GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.datapins, GPIO.OUT, initial=GPIO.LOW)
    
    def set_data_bits(self, byte):
        for i, pin in enumerate(self.datapins):
            filtered = (byte >> i) & 0x1
            GPIO.output(pin, filtered)

    def send_instruction(self, byte):
        GPIO.output(self.ENABLE, GPIO.HIGH) # make sure enable is off before writing
        GPIO.output(self.RS, GPIO.LOW) # set RS to instruction input
        self.set_data_bits(byte) # write byte
        GPIO.output(self.ENABLE, GPIO.LOW) # send
        time.sleep(DELAY) # wait for LCD to process
        GPIO.output(self.ENABLE, GPIO.HIGH) # turn enable back off


    def send_character(self, byte):
        GPIO.output(self.ENABLE, GPIO.HIGH) # make sure enable is off before writing
        GPIO.output(self.RS, GPIO.HIGH) # set RS to data input
        self.set_data_bits(byte) # write byte
        GPIO.output(self.ENABLE, GPIO.LOW) # send
        time.sleep(DELAY) # wait for LCD to process
        GPIO.output(self.ENABLE, GPIO.HIGH) # turn enable back off

    def init_LCD(self):
        # function set
        self.send_instruction(0x38) #0b0011 1000
        # display on
        self.send_instruction(0x0f) # 0b0000 1111
        # clear display & cursor home
        self.send_instruction(0x01) #0b0000 0001

    def send_message(self, message):
        for byte in bytearray(message, encoding='utf8'):
            self.send_character(byte)
    
    def jump_to_second_line(self):
        self.send_instruction(0x80 | 0x40)