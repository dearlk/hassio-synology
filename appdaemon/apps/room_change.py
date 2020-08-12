import appdaemon.plugins.hass.hassapi as hass
#import appdaemon.plugins.mqtt.mqttapi as mqtt
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
import json
import os.path
from pathlib import Path
from os import path
import operator
import io
import sys,getopt
import myglobals
# RoomChange App
#
# Args:
#

class RoomChangeApp(hass.Hass):

  def initialize(self):
    self.sensor = self.args["sensor"]
    self.listen_state(self.room_changed, entity=self.sensor)


  def room_changed (self, entity, attribute, old, new, kwargs):
    if old == new:
      return
    else:
      data= "{} has moved into {}".format(self.sensor.split(".")[1].split("_")[0], new)
      self.notify(data, name=myglobals.notify_service)
      self.log(data)


