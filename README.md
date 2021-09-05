# larc

WIP programmable hw midi controller

currently only controlling a few HDPL-1414:
 - raspi controlling w/ 3 IO pins 2 74HC595 daisy chained (outputs 9 pins for A0-1 + D0-6)
 - raspi controlling each HPDL-1414 WRT pin with a dedicated IO

this approach seems more viable: https://github.com/RoelandR/HPDL-1414-board


## References

[HPDL-1414 datasheet](http://www.farnell.com/datasheets/76528.pdf)
[HPDL-1414 arduino library](https://github.com/marecl/HPDL1414/blob/master/src/HPDL1414.cpp)
