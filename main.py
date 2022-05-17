#!/usr/bin/env python3

import os
from time import sleep
import math

import RPi.GPIO as gpio
gpio.setwarnings(False)

from lib.shifter import Shifter
from lib.mcp3008 import MCP3008
from lib.hpdl1414 import hpdl_blank, \
    hpdl_write_word, multi_hpdl_write_word, \
    hpdl_loop_words, multi_hpdl_loop_words


## ------------------------------------------------------------------------
# RASPI GPIO - CONF

# 14 - DS / SER    - serial data input          -  data pin
SHIFTER_DATA = 11
# 11 - SH_CP / SCK - shift register clock pin   -  clock pin
SHIFTER_CLK = 12
# 12 - ST_CP / RCK - storage register clock pin -  latch pin
SHIFTER_LATCH = 13

# HPDL-1414 WRT pins
WRT1414_1 = 15
WRT1414_2 = 16

kbd_swtch = 10

# MCP3008 (ADC) pins, using HW SPI0
MCP3008_SPI_BUS   = 0
MCP3008_SPI_DEVICE = 0
# raspi 19 (MOSI) -> DIN
# raspi 21 (MISO) -> DOUT
# raspi 21 (SCLK) -> CLK
# raspi 21 (CE0)  -> CS/SHDN


## ------------------------------------------------------------------------
# RASPI GPIO - SETUP

gpio.setmode(gpio.BOARD)

shifter = Shifter(data=SHIFTER_DATA, clock=SHIFTER_CLK, latch=SHIFTER_LATCH)

gpio.setup(WRT1414_1, gpio.OUT)
gpio.setup(WRT1414_2, gpio.OUT)
# disable write
gpio.output(WRT1414_1, gpio.HIGH)
gpio.output(WRT1414_2, gpio.HIGH)

gpio.setup(kbd_swtch, gpio.IN, pull_up_down=gpio.PUD_DOWN)

adc = MCP3008(bus=MCP3008_SPI_BUS, device=MCP3008_SPI_DEVICE)


## ------------------------------------------------------------------------
## MAIN

def main():
    pause = 0.2
    running = True

    char_row_index = 0
    digit_index = 0

    words = []
    with open(os.path.abspath(os.path.dirname(__file__)) + '/rsc/words.txt') as f:
        for w in f:
            words.append(w.strip().lower())

    def kbd_swtch_pressed():
        return gpio.input(kbd_swtch) == gpio.HIGH
    try:
        # reset shifter data
        shifter.clear()

        # blank displays
        hpdl_blank(WRT1414_1, shifter)
        hpdl_blank(WRT1414_2, shifter)

        # words = ["", "ceci", "est", "un", "test"]
        # hpdl_loop_words(WRT1414_1, shifter, words, infinite=True)

        # words = ["tulipe", "patate", "canard", "tomate"]
        # multi_hpdl_loop_words([WRT1414_1, WRT1414_2], shifter, words, infinite=False, align='center')

        # words = ["tulipe", "patate", "canard", "tomate", "limace", "violon", "carotte", "lasagne", "salade"]
        # multi_hpdl_loop_words([WRT1414_1, WRT1414_2], shifter, words, infinite=True, align='center',
        #                       predicate=kbd_swtch_pressed)

        # hpdl_loop_charset(WRT1414_1, shifter, 0, infinite=False)

        # multi_hpdl_write_word([WRT1414_1, WRT1414_2], shifter, "eignbahn")
        # multi_hpdl_write_word([WRT1414_1, WRT1414_2], shifter, "nornzine")


        while True:
            # v = math.log(adc.read(0) + 0.01)
            v1 = adc.read(0)
            if v1 >= 1000:
                v1 = 999
            multi_hpdl_write_word([WRT1414_1, WRT1414_2], shifter, words[v1])
            sleep(0.1)

    except KeyboardInterrupt:
        print("Bye")
        running = False


if __name__=="__main__":
    main()
