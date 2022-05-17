#!/usr/bin/env python3

import RPi.GPIO as gpio
from collections import OrderedDict
from time import sleep

gpio.setwarnings(False)


## ------------------------------------------------------------------------
## CORE - BINARY

def hexp(v):
    padding = 8
    return '0x{0:0{1}X}'.format(v, padding)

def binp(v):
    return format(v, '#010b')

def is_bit_on(v, index):
    mask = 0b1 << index
    return (mask & v) > 0


## ------------------------------------------------------------------------
## CORE - STR

### Returns ne version of `word` that fits in `length` digits
def truncate_align_word(word, length, align='left'):
    if align == 'right':
        op = '>'
    elif align == 'center':
        op = '^'
    else:
        op = '<'
        # align
    word = ('{:' + op + str(length) + '}').format(word)
    # truncate
    word = word[0:length]
    return word


## ------------------------------------------------------------------------

kbd_swtch = 10

# HPDL-1414 WRT pins
wrt1414_1 = 15
wrt1414_2 = 16


## ------------------------------------------------------------------------
## 74HC595

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
            r = 7 - r # we need to push from MSB to LSB
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


## ------------------------------------------------------------------------
## HPDL-1414 - TIMING DELAYS

# write delay
WRT1414_TWD = 20 // 1000000000
# write time
WRT1414_TW = 130 // 1000000000
# address setup time (twd + td)
WRT1414_TAS = 150 // 1000000000

# address hold time
WRT1414_TAH = 50 // 1000000000


## ------------------------------------------------------------------------
## HPDL-1414 - DICT

CHAR_ROWS_PREFIXES = [0b010, 0b011, 0b100, 0b101]
DIGIT_SEL_PREFIXES = [[0, 0], [0, 1], [1, 0], [1, 1]]

HPDL_CHARS = OrderedDict({
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
})


## ------------------------------------------------------------------------
## HPDL-1414 - FNS

### Make HPDL-1414 w/ WRT `pin` apply the value at its pins (An, Dn)
def hpdl_write(pin):
    gpio.output(pin, gpio.LOW)
    sleep(WRT1414_TWD)
    sleep(WRT1414_TW)
    sleep(WRT1414_TAH)
    gpio.output(pin, gpio.HIGH)

### Write raw `value` to HPDL w/ WRT `pin`, via `shifter`
### `value` is typically an array of 8-sized bitmaps
def hpdl_write_value(pin, shifter, value):
    # shifter.clear()
    shifter.setValue(value)
    hpdl_write(pin)

### Write `char` to `digit` of HPDL w/ WRT `pin`, via `shifter`
def hpdl_write_char(pin, shifter, digit, char):
    d = DIGIT_SEL_PREFIXES[::-1][digit]
    c_pos = HPDL_CHARS[char]
    c = (CHAR_ROWS_PREFIXES[c_pos[0]] << 4) + c_pos[1] + (d[1] << 7)
    raw_v = [d[0], c]
    hpdl_write_value(pin, shifter, raw_v)

def hpdl_blank_char(pin, shifter, digit):
    hpdl_write_char(pin, shifter, digit, " ")

### Write 4 char `word` to HPDL w/ WRT `pin`, via `shifter`
def hpdl_write_word(pin, shifter, word, align='left'):
    word = truncate_align_word(word, 4, align)
    for i, char in enumerate(word):
        hpdl_write_char(pin, shifter, i, char)

def hpdl_blank(pin, shifter):
    hpdl_write_word(pin, shifter, "")


## ------------------------------------------------------------------------
## MULTI HPDL-1414 - FNS

def multi_hpdl_write_word(pins, shifter, word, align='left'):
    nb_chars = len(pins) * 4
    word = truncate_align_word(word, nb_chars, align)
    for i, pin in enumerate(pins[::-1]):
        char_shift = i*4
        hpdl_write_word(pin, shifter, word[0+char_shift:4+char_shift])


## ------------------------------------------------------------------------
## HPDL-1414 - DEBUG FNS

def hpdl_loop_charset(pin, shifter, digit, pause=0.2, infinite=True):
    chars = list(HPDL_CHARS.keys())
    c_i = 0
    running = True
    while running == True:
        try:
            hpdl_write_char(pin, shifter, digit, chars[c_i])
            sleep(pause)
            c_i = (c_i + 1) % len(chars)
            if not infinite and c_i == 0:
                running=False
        except KeyboardInterrupt:
            running=False

def hpdl_loop_words(pin, shifter, words, pause=0.2, infinite=True, align='left'):
    w_i = 0
    running = True
    while running == True:
        try:
            word = words[w_i]
            hpdl_write_word(pin, shifter, word, align=align)
            sleep(pause)
            w_i = (w_i + 1) % len(words)
            if not infinite and w_i == 0:
                running=False
        except KeyboardInterrupt:
            running=False

def multi_hpdl_loop_words(pins, shifter, words, pause=0.2, infinite=True, align='left', predicate=None):
    w_i = 0
    running = True
    while running == True:
        try:
            word = words[w_i]
            multi_hpdl_write_word(pins, shifter, word, align=align)
            if predicate != None and not predicate():
                continue
            else:
                sleep(pause)
            w_i = (w_i + 1) % len(words)
            if not infinite and w_i == 0:
                running=False
        except KeyboardInterrupt:
            running=False


## ------------------------------------------------------------------------
## MAIN

def main():
    pause = 0.2
    gpio.setmode(gpio.BOARD)
    shifter = Shifter()
    running = True

    char_row_index = 0
    digit_index = 0

    gpio.setup(kbd_swtch, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    def kbd_swtch_pressed():
        return gpio.input(kbd_swtch) == gpio.HIGH

    gpio.setup(wrt1414_1, gpio.OUT)
    gpio.setup(wrt1414_2, gpio.OUT)
    # disable write
    gpio.output(wrt1414_1, gpio.HIGH)
    gpio.output(wrt1414_2, gpio.HIGH)

    shifter.clear()

    # blank
    hpdl_blank(wrt1414_1, shifter)
    hpdl_blank(wrt1414_2, shifter)

    # words = ["", "ceci", "est", "un", "test"]
    # hpdl_loop_words(wrt1414_1, shifter, words, infinite=False)

    words = ["tulipe", "patate", "canard", "tomate", "limace", "violon", "carotte", "lasagne", "salade"]
    multi_hpdl_loop_words([wrt1414_1, wrt1414_2], shifter, words, infinite=True, align='center',
                          predicate=kbd_swtch_pressed)

    # hpdl_loop_charset(wrt1414_1, shifter, 0, infinite=False)

    multi_hpdl_write_word([wrt1414_1, wrt1414_2], shifter, "eignbahn")

    running = False


if __name__=="__main__":
    main()
