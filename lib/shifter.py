from time import sleep
import RPi.GPIO as gpio
from lib.binutils import is_bit_on


## ------------------------------------------------------------------------
## 74HC595

class Shifter():

    def __init__(self, data=11, clock=12, latch=13):
        self.pause = 0
        self.data = data
        self.clock = clock
        self.latch = latch
        self.setupBoard()

    def tick(self):
        gpio.output(self.clock, gpio.HIGH)
        sleep(self.pause)
        gpio.output(self.clock, gpio.LOW)
        sleep(self.pause)

    def setByte(self, b):
        for r in range(8):
            r = 7 - r # we need to push from MSB to LSB
            if (is_bit_on(b, r)):
                gpio.output(self.data, gpio.HIGH)
            else:
                gpio.output(self.data, gpio.LOW)
            Shifter.tick(self)

    def setValue(self, byte_l):
        gpio.output(self.latch, gpio.LOW)
        for b in byte_l:
            Shifter.setByte(self, b)
        gpio.output(self.latch, gpio.HIGH)

    def clear(self):
        gpio.output(self.latch, gpio.LOW)
        Shifter.tick(self)
        gpio.output(self.latch, gpio.HIGH)

    def setupBoard(self):
        gpio.setup(self.data, gpio.OUT)
        gpio.output(self.data, gpio.LOW)
        gpio.setup(self.clock, gpio.OUT)
        gpio.output(self.clock, gpio.LOW)
        gpio.setup(self.latch, gpio.OUT)
        gpio.output(self.latch, gpio.HIGH)
