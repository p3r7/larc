#!/usr/bin/env python3

import RPi.GPIO as gpio
from time import sleep

gpio.setwarnings(False)


## ------------------------------------------------------------------------
## BINARY HELPERS

def hexp(v):
    padding = 8
    return '0x{0:0{1}X}'.format(v, padding)

def binp(v):
    return format(v, '#010b')

def is_bit_on(v, index):
    mask = 0b1 << index
    return (mask & v) > 0

### NB: on my specific variant of the 74HC595, Q pin indexes are all reversed...
def normalize_bit_index(index):
    return 7 - index


## ------------------------------------------------------------------------


wrt1414 = 15
# write delay
wrt1414_twd = 20 // 1000000000
# write time
wrt1414_tw = 130 // 1000000000
# address setup time (twd + td)
wrt1414_tas = 150 // 1000000000

# address hold time
wrt1414_tah = 50 // 1000000000


class Shifter():

    # 14 - DS / SER    - serial data input          -  data pin
    inputB=11
    # 11 - SH_CP / SCK - shift register clock pin   -  clock pin
    clock=12
    # 12 - ST_CP / RCK - storage register clock pin -  latch pin
    latch=13

    # NB:
    # 13 - OE / G      (output enabled)  -> on GND to enable
    # 10 - MR / SCL    (master reclear)  -> on 5V to disable

    def __init__(self):
        self.setupBoard()
        self.pause=0
    def tick(self):
        gpio.output(Shifter.clock, gpio.HIGH)
        sleep(self.pause)
        gpio.output(Shifter.clock, gpio.LOW)
        sleep(self.pause)

    # def setValue(self,value):
    #     for i in range(24):
    #         bitwise=0x800000>>i
    #         bit=bitwise&value
    #         if (bit==0):
    #             gpio.output(Shifter.inputB,gpio.LOW)
    #         else:
    #             gpio.output(Shifter.inputB,gpio.HIGH)
    #         Shifter.tick(self)
    def setValue(self,value):
        gpio.output(Shifter.latch, gpio.LOW)
        for r in range(8):
            r = normalize_bit_index(r) ## software fix for some variants of the shift register
            if (is_bit_on(value, r)):
                gpio.output(Shifter.inputB, gpio.HIGH)
            else:
                gpio.output(Shifter.inputB,gpio.LOW)
            Shifter.tick(self)
        gpio.output(Shifter.latch, gpio.HIGH)

    def clear(self):
        gpio.output(Shifter.latch, gpio.LOW)
        Shifter.tick(self)
        gpio.output(Shifter.latch, gpio.HIGH)

    def setupBoard(self):
        gpio.setup(Shifter.inputB, gpio.OUT)
        gpio.output(Shifter.inputB, gpio.LOW)
        gpio.setup(Shifter.clock, gpio.OUT)
        gpio.output(Shifter.clock, gpio.LOW)
        gpio.setup(Shifter.latch, gpio.OUT)
        gpio.output(Shifter.latch, gpio.HIGH)


def write_value(shifter, value):
    shifter.clear()

    gpio.output(wrt1414, gpio.LOW)
    sleep(wrt1414_twd)

    shifter.setValue(value)

    # sleep(1)
    sleep(wrt1414_tw)

    sleep(wrt1414_tah)
    gpio.output(wrt1414, gpio.HIGH)



def main():
    pause=0.2
    gpio.setmode(gpio.BOARD)
    shifter=Shifter()
    running=True

    gpio.setup(wrt1414, gpio.OUT)

    shifter.clear()


    char_rows_prefixes = [0b010, 0b011, 0b100, 0b101]
    char_row_index = 0
    digit_sel_prefixes = [0b00, 0b01, 0b10, 0b11]

    char_col = 0b0000
    while running==True:
        try:

            v = (char_rows_prefixes[char_row_index] << 4) + char_col

            print(binp(v) + ' | ' + hex(v) + ' | ' + str(v))
            write_value(shifter, v)
            sleep(pause)

            char_col += 1
            if char_col > 0b1111:
                char_col = 0b0000
                char_row_index = (char_row_index + 1) % 4

        except KeyboardInterrupt:
            running=False


if __name__=="__main__":
    main()
