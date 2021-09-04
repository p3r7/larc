#!/usr/bin/env python3

import RPi.GPIO as gpio
from time import sleep

gpio.setwarnings(False)

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
    clearPin=13

    # NB:
    # 13 - OE / G      (output enabled)  -> on GND to enable
    # 10 - MR / SCL    (master reclear)  -> on 5V to disable

    def __init__(self):
        self.setupBoard()
        self.pause=0
    def tick(self):
        gpio.output(Shifter.clock,gpio.HIGH)
        sleep(self.pause)
        gpio.output(Shifter.clock,gpio.LOW)
        sleep(self.pause)

    def setValue(self,value):
        for i in range(24):
            bitwise=0x800000>>i
            bit=bitwise&value
            if (bit==0):
                gpio.output(Shifter.inputB,gpio.LOW)
            else:
                gpio.output(Shifter.inputB,gpio.HIGH)
            Shifter.tick(self)

    def clear(self):
        gpio.output(Shifter.clearPin,gpio.LOW)
        Shifter.tick(self)
        gpio.output(Shifter.clearPin,gpio.HIGH)

    def setupBoard(self):
        gpio.setup(Shifter.inputB,gpio.OUT)
        gpio.output(Shifter.inputB,gpio.LOW)
        gpio.setup(Shifter.clock,gpio.OUT)
        gpio.output(Shifter.clock,gpio.LOW)
        gpio.setup(Shifter.clearPin,gpio.OUT)
        gpio.output(Shifter.clearPin,gpio.HIGH)


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
    pause=0.4
    gpio.setmode(gpio.BOARD)
    shifter=Shifter()
    running=True

    gpio.setup(wrt1414, gpio.OUT)

    # start_v = 0x0000000
    # end_v = 0x0FFFFFF

    # start_v = 0x11 # 17
    # end_v = 0x2f   # 47

    # start_v = 0x50
    # end_v = 0x0FFFFFF

    # start_v = 0x52
    # end_v = 0x70



    start_v = 0b0100001
    end_v =   0b0101111

    start_v = 0b10000000
    end_v =   0b10000000


    # - 0b0100000 - " "
    # - 0b0100001 - inverted F
    # - 0b0100010 - $

    # 0
    # expected 0b0110000
    # actual   0b0101000

    # 3
    # expected 0b0110011
    # actual   0b0101001
    # -> wtf?



    v = start_v

    while running==True:
        try:

            print(bin(v) + ' | ' + hex(v) + ' | ' + str(v))
            write_value(shifter, v)
            sleep(pause)

            v += 1
            if v > end_v:
                v = start_v

            # write_value(shifter, 1)
            # sleep(pause)

            # print("switch")

            # write_value(shifter, 0x0AAAAAA)
            # sleep(pause)

            # print("switch")

            # write_value(shifter, 0x0555555)
            # sleep(pause)

            # print("switch")



            # gpio.output(wrt1414, gpio.LOW)
            # sleep(wrt1414_twd)

            # shifter.clear()
            # shifter.setValue(1)
            # # shifter.setValue(0x0AAAAAA)
            # # shifter.setValue(0x0555555)

            # # sleep(1)
            # sleep(wrt1414_tw)

            # sleep(wrt1414_tah)
            # gpio.output(wrt1414, gpio.HIGH)


            # # shifter.clear()
            # # shifter.setValue(0x0AAAAAA)
            # # sleep(pause)
            # # shifter.clear()
            # # shifter.setValue(0x0555555)
            # # sleep(pause)

        except KeyboardInterrupt:
            running=False


if __name__=="__main__":
    main()
