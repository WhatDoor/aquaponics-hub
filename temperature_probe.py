#!/usr/bin/python
import spidev
import MAX6675
from time import sleep

cs_pin = 24
clock_pin = 23
data_pin = 22
units = "c"
thermocouple = MAX6675.MAX6675(cs_pin, clock_pin, data_pin, units)


def take_temperature():
    try:
        tc = thermocouple.get()        
        print(tc)
    except MAX6675.MAX6675Error as e:
        tc = "Error: "+ e.value
        print("tc: {}".format(tc))
    return tc
