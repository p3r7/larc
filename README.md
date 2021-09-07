# larc

WIP programmable hw midi controller

currently only controlling a few **HDPL-1414** 14 segment displays:
 - **raspi** controlling w/ 3 IO pins 2 **74HC595** daisy chained (outputs 9 pins for A0-1 + D0-6)
 - **raspi** controlling each **HPDL-1414** WRT pin with a dedicated IO

alternatively, could use a MCP23017 (i2c) or MCP23S17 (SPI) ([datasheet](https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf)) like [this project](https://github.com/RoelandR/HPDL-1414-board) for a (slightly smaller form factor & fewer raspi pins used.


## References

**Raspberry Pi**:
 - [Raspberry Pi GPIO pinouts](https://pinout.xyz/pinout/wiringpi#)

**HPDL-1414**:
 - [datasheet](http://www.farnell.com/datasheets/76528.pdf)
 - [arduino library](https://github.com/marecl/HPDL1414/blob/master/src/HPDL1414.cpp)

**74HC595**:
 - [datasheet](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf)
 - [official arduino tutorial](https://www.arduino.cc/en/Tutorial/Foundations/ShiftOut)
 - [arduino tutorial on lastminuteengineers.com](https://lastminuteengineers.com/74hc595-shift-register-arduino-tutorial/)
