import spidev

class SpiClass:
    
    def __init__(self, bus=0, device=0):
        self._bus = bus
        self._device = device
        self._spi = spidev.SpiDev()
        self._spi.open(0, 0)
        self._spi.max_speed_hz = 5000

    def read_channel(self, ch):
        # example: ch = 1 (0001), 1000 | 0001 = 1001 << 4 -> 10010000
        # example: ch = 3 (0011), 1000 | 0011 = 1011 << 4 -> 10110000
        bytes_out = [0x1, (1000 | ch) << 4, 0x0]

        res = self._spi.xfer(bytes_out) # response
        # filter eerste 2 bits van res[2] (bit 8 en bit 9), 
        # shift 8 naar links, combineer met res[1] (bit 0 tot bit 7)
        return ((res[1] & 0b0011) << 8) | res[2] #example: [00000011, 11111111] -> 1111111111

    def closespi(self):
        self._spi.close()

from RPi import GPIO
import time

def main():
    GPIO.setmode(GPIO.BCM)
    try:
        obj = SpiClass()
        # setup servo PWM
        while True:
            value = obj.read_channel(0) # read bits (0-1023)
            converted = ((value / 1023.0) * (12.0 -  3.0)) + 3 #convert from 0-1023 to 3.0 - 12.0

            print(converted)
            time.sleep(0.1)
    except KeyboardInterrupt:
        p.stop()
        pass
    finally:
        obj.closespi()
        GPIO.cleanup()


if __name__ == '__main__':
    main()