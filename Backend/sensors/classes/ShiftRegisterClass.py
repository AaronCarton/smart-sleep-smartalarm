import time
from RPi import GPIO

# default pin numbers (BCM) - pas aan indien nodig
DS = 20  # serial data
OE = 16  # output enable (active low)
STCP = 12  # storage register clock pulse
SHCP = 24  # shift register clock pulse
MR = 23  # master reset (active low)


DELAY = 0.00001

class ShiftRegister:
    def __init__(self, ds_pin=DS, shcp_pin=SHCP, stcp_pin=STCP, mr_pin=MR, oe_pin=OE):
       
        self.ds_pin = ds_pin
        self.shcp_pin = shcp_pin
        self.stcp_pin = stcp_pin
        self.mr_pin = mr_pin
        self.oe_pin = oe_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([ds_pin, oe_pin, shcp_pin, stcp_pin, mr_pin], GPIO.OUT, initial=GPIO.LOW)
        # volgende kan ook
        # for pin in ds_pin, oe_pin, shcp_pin, stcp_pin, mr_pin:
        #     GPIO.setup(pin, GPIO.OUT)
        #     GPIO.output(pin, GPIO.LOW)
        GPIO.output(self.mr_pin, GPIO.HIGH)

    def write_bit(self, value):
        # vul hier zelf aan, gebruik self.ds_pin en self.shcp_pin als pin variabelen  
        GPIO.output(self.ds_pin, value)
        time.sleep(DELAY)
        GPIO.output(self.shcp_pin, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(self.shcp_pin, GPIO.LOW)
    
    def copy_to_storage_register(self):
        # vul hier zelf aan, gebruik self.ds_pin en self.shcp_pin als pin variabelen  
        GPIO.output(self.stcp_pin, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(self.stcp_pin, GPIO.LOW)

    def write_byte(self, value):
        # vul hier zelf aan: code om een byte uit te splitsen in bits...
        for x in range(8, -1, -1):
            # 0b10000110
            bit = (value >> x) & 0x01
            # print(bin(bit))
            self.write_bit(bit)

    @property
    def output_enabled(self):
        return not GPIO.input(self.oe_pin)

    @output_enabled.setter
    def output_enabled(self, value):
        GPIO.output(self.oe_pin, not value)

    def reset_shift_register(self):
        GPIO.output(self.mr_pin, GPIO.LOW)
        time.sleep(DELAY)
        GPIO.output(self.mr_pin, GPIO.HIGH)
        time.sleep(DELAY)

    def reset_storage_register(self):
        
        self.reset_shift_register()
        self.copy_to_storage_register()


def shiftreg_demo():
   
    shreg = ShiftRegister()
    value = 1
    while value < 0x100:
        shreg.write_byte(value)
        shreg.copy_to_storage_register()
        time.sleep(1)
        value <<= 1

def teller():
    shreg = ShiftRegister()
    for i in range (0,16):
        shreg.write_byte(SEGMENTS[i])
        shreg.copy_to_storage_register()
        time.sleep(1)


# Juiste bit voor elk segment: vul/pas aan
A = 1 << 0
B = 1 << 1
C = 1 << 2
D = 1 << 3
E = 1 << 4
F = 1 << 5
G = 1 << 6
DP = 1 << 7

# Juist segment voor elk (hex) cijfer: vul/pas aan
SEGMENTS = {
    0x0: A | B | C | D | E | F,
    0x1: B | C,
    0x2: A | B | G | E | D,
    0x3: A | B | C | D | G,
    0x4: F | G | B | C,
    0x5: A | F | G | C | D,
    0x6: A | C | D | E | F | G,
    0x7: A | B | C,
    0x8: A | B | C | D | E | F | G,
    0x9: A | B | C | D | F | G,
    0xA: A | B | C | E | F | G,
    0xb: C | D | E | F | G,
    0xC: A | F | E | D,
    0xd: B | C | D | E | G,
    0xE: A | F | G | E | D,
    0xF: A | G | F | E,
}


class SevenSegment:
    def __init__(self, shreg= ShiftRegister):
        self.shreg = shreg
        self.shreg.reset_shift_register()

    def show_segments(self, value):
        """
        Show byte segments on the display
        :param value: byte
        :return: None
        """
        self.shreg.write_byte(value)
        self.shreg.copy_to_storage_register()
        self.shreg.output_enabled = True

    def show_digit(self, value, with_dp=False):
        """
        Show dec/hex number on the display
        :param value: digit(int) (0-0xF)
        :param with_dp: (boolean) show decimal point
        :return: None
        """
        segments = SEGMENTS[value]
        if with_dp:
            segments |= DP
        self.show_segments(segments)


def seven_segment_demo():
    """
    Show each number (0-0xF) one by one in 1 sec intervals
    :return: None
    """
    shreg = ShiftRegister()
    display = SevenSegment(shreg)
    for i in range(17):
        display.show_digit(i)
        time.sleep(1)


class SevenSegmentCascade(SevenSegment):
    def show_list(self, values):
        """
        Show a list of bytes on any number of displays
        """
        for value in values:
            self.shreg.write_byte(value)
        self.shreg.copy_to_storage_register()

    def show_hex_digits(self, value):
        """
        Show <value> as hexadecimal number on any number of displays
        :param value: integer
        :return: None
        """
        while value:
            self.shreg.write_byte(SEGMENTS[value & 0xf])
            value >>= 4
        self.shreg.copy_to_storage_register()

    def show_dec_digits(self, value):
        """
        Show <value> in base 10 on any number of displays
        :param value: integer
        :return: None
        """
        while value:
            self.shreg.write_byte(SEGMENTS[value % 10])
            value //= 10
        self.shreg.copy_to_storage_register()

    def show_float(self, value):
        """
        Show <value> with one decimal digit (eg. 4.2)
        :param value: float
        :return: None
        """
        self.shreg.write_byte(SEGMENTS[value % 1])
        self.shreg.write_byte(DP | SEGMENTS[value // 1])


def main():
    GPIO.setmode(GPIO.BCM)
    try:
        # Hier kan je jouw functies/klassen oproepen om ze te testen
        #shiftreg_demo()
        seven_segment_demo()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()