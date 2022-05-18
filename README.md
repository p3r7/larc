# larc

WIP programmable hw midi controller

currently only controlling a few **HDPL-1414** 14 segment displays:
 - **raspi** controlling w/ 3 IO pins 2 **74HC595** daisy chained (outputs 9 pins for A0-1 + D0-6)
 - **raspi** controlling each **HPDL-1414** WRT pin with a dedicated IO
 - **MCP3008** ADC for allowing raspi to read value of ALPS analog faders
 - Cherry MX keyswitches

for driving the segment displays, could alternatively use a MCP23017 (i2c) or MCP23S17 (SPI) ([datasheet](https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf)) like [this project](https://github.com/RoelandR/HPDL-1414-board) to save a few raspi pins (but w/ bigger form factor & less control over latch sync).


## Deps

Using [spidev](https://github.com/doceme/py-spidev), installed through apt (`python3-spidev`).

Also tried [Adafruit's legacy MCP3008 lib](https://github.com/adafruit/Adafruit_Python_MCP3008.git) but had trouble getting it to work.


## References

**Raspberry Pi**:
 - [Raspberry Pi GPIO pinouts](https://pinout.xyz/pinout/wiringpi#)

HP **HPDL-1414** (aka Litronix/Siemens DL1414T):
 - [datasheet](http://www.farnell.com/datasheets/76528.pdf)
 - [arduino library](https://github.com/marecl/HPDL1414/blob/master/src/HPDL1414.cpp)

**74HC595**:
 - [datasheet](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf)
 - [official arduino tutorial](https://www.arduino.cc/en/Tutorial/Foundations/ShiftOut)
 - [arduino tutorial on lastminuteengineers.com](https://lastminuteengineers.com/74hc595-shift-register-arduino-tutorial/)

for targeting Lexicon MPX1, see [this repo](https://github.com/p3r7/lexicon-mpx1-sysex-tests/blob/main/larc.py).
