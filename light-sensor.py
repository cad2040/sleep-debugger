#!/usr/bin/env python
import os
import sys
from atexit import register
from math import sqrt, pow
import json
from time import sleep, time
from struct import unpack
import Adafruit_VCNL40xx
from influxdb import InfluxDBClient
from sensor_lock import SensorLock

LOCK_FILE = "/var/lock/sleep-debugger-light-sensor.lock"

class LightSensor(object):

    INFLUX_HOST = "10.1.1.2"
    INFLUX_PORT = 8086
    def __init__(self):

        self.influx = InfluxDBClient(self.INFLUX_HOST, self.INFLUX_PORT, "root", "root", "sleep")
        self.vcnl = Adafruit_VCNL40xx.VCNL4010(busnum=1)
        self.lock = SensorLock(LOCK_FILE)

    def _read_data_point(self):
        return self.vcnl.read_ambient()

    def _log(self, point):
        json_body = [
            {
                "measurement": "light",
                "tags": 
                {
                    "sleeper": "mayhem",
                },
                "fields": 
                {
                    "light": point,
                }
            }
        ]
        self.influx.write_points(json_body)

    def run(self):
        if not self.lock.allowed_to_start():
            sys.exit(-1)

        self.lock.create()

        while True:
            pt = int(self._read_data_point())
            #print "ambient: %d" % pt
            self._log(pt)
            sleep(10)

if __name__ == "__main__":

    print "starting sleep debugger light sensor logger"
    ls = LightSensor()
    try:
        ls.run()
    except KeyboardInterrupt:
        pass
