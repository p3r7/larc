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

HPDL_CHARS = {
    # row 1
    ' ': [0 , 0],
    '!': [0 , 1],
    '"': [0 , 2],
    '#': [0 , 3],
    '$': [0 , 4],
    '%': [0 , 5],
    '&': [0 , 6],
    "'": [0 , 7],
    '<': [0 , 8],
    '>': [0 , 9],
    '*': [0 , 10],
    '+': [0 , 11],
    ',': [0 , 12],
    '-': [0 , 13],
    '.': [0 , 14],
    '/': [0 , 15],

    # row 2
    '0': [1 , 0],
    '1': [1 , 1],
    '2': [1 , 2],
    '3': [1 , 3],
    '4': [1 , 4],
    '5': [1 , 5],
    '6': [1 , 6],
    "7": [1 , 7],
    '8': [1 , 8],
    '9': [1 , 9],
    ':': [1 , 10],
    ';': [1 , 11],
    '<=': [1 , 12],
    '=': [1 , 13],
    '>=': [1 , 14],
    '?': [1 , 15],

    # row 3
    '@': [2 , 0],
    'a': [2 , 1],
    'b': [2 , 2],
    'c': [2 , 3],
    'd': [2 , 4],
    'e': [2 , 5],
    'f': [2 , 6],
    "g": [2 , 7],
    'h': [2 , 8],
    'i': [2 , 9],
    'j': [2 , 10],
    'k': [2 , 11],
    'l': [2 , 12],
    'm': [2 , 13],
    'n': [2 , 14],
    'o': [2 , 15],

    # row 4
    'p': [3 , 0],
    'q': [3 , 1],
    'r': [3 , 2],
    's': [3 , 3],
    't': [3 , 4],
    'u': [3 , 5],
    'v': [3 , 6],
    "w": [3 , 7],
    'x': [3 , 8],
    'y': [3 , 9],
    'z': [3 , 10],
    '(': [3 , 11],
    '\\': [3 , 12],
    ')': [3 , 13],
    '^': [3 , 14],
    '_': [3 , 15],

}

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


    def setByte(self, b):
        for r in range(8):
            r = normalize_bit_index(r) ## software fix for some variants of the shift register
            if (is_bit_on(b, r)):
                gpio.output(Shifter.inputB, gpio.HIGH)
            else:
                gpio.output(Shifter.inputB,gpio.LOW)
            Shifter.tick(self)

    def setValue(self, byte_l):
        gpio.output(Shifter.latch, gpio.LOW)
        for b in byte_l:
            Shifter.setByte(self, b)
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
    pause = 0.2
    gpio.setmode(gpio.BOARD)
    shifter = Shifter()
    running = True

    char_rows_prefixes = [0b010, 0b011, 0b100, 0b101]
    char_row_index = 0
    digit_sel_prefixes = [[0, 0], [0, 1], [1, 0], [1, 1]]
    digit_index = 0

    gpio.setup(wrt1414, gpio.OUT)

    shifter.clear()

    # blank
    c_pos = HPDL_CHARS[" "]
    c = (char_rows_prefixes[c_pos[0]] << 4) + c_pos[1]
    for d in digit_sel_prefixes:
        shifter.setValue([d[0], c + (d[1] << 7)])
        gpio.output(wrt1414, gpio.LOW)
        sleep(wrt1414_twd)
        sleep(wrt1414_tw)
        sleep(wrt1414_tah)
        gpio.output(wrt1414, gpio.HIGH)
    sleep(0.1)


    words = ["   ", "let ", " me ", "show", "you ", "some", "dust"]
    w_i = 0
    while(1):
        word = words[w_i]
        for i, char in enumerate(word):
            d = digit_sel_prefixes[::-1][i]
            c_pos = HPDL_CHARS[char]
            c = (char_rows_prefixes[c_pos[0]] << 4) + c_pos[1] + (d[1] << 7)
            shifter.setValue([d[0], c])

            gpio.output(wrt1414, gpio.LOW)
            sleep(wrt1414_twd)
            sleep(wrt1414_tw)
            sleep(wrt1414_tah)
            gpio.output(wrt1414, gpio.HIGH)

        sleep(0.5)
        w_i = (w_i + 1) % len(words)


    running = False


    char_col = 0b0000
    while running==True:
        try:

            d = digit_sel_prefixes[digit_index]
            v = (char_rows_prefixes[char_row_index] << 4) + char_col + (d[1] << 7)

            print(binp(v + (d[0] << 8)) + ' | ' + hex(v) + ' | ' + str(v))
            shifter.setValue([d[0], c])

            gpio.output(wrt1414, gpio.LOW)
            sleep(wrt1414_twd)
            sleep(wrt1414_tw)
            sleep(wrt1414_tah)
            gpio.output(wrt1414, gpio.HIGH)

            sleep(pause)

            char_col += 1
            if char_col > 0b1111:
                char_col = 0b0000
                char_row_index = (char_row_index + 1) % 4

        except KeyboardInterrupt:
            running=False


if __name__=="__main__":
    main()
