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

class RoomLightsAutomation(hass.Hass):

  def initialize(self):
    self.room = self.args["room"]
    self.motion_sensor = self.args["motion_sensor"]
    self.daylight_sensor = self.args["daylight_sensor"]
    self.log("room={},motion_sensor={},daylight_sensor={}".format(self.room,self.motion_sensor,self.daylight_sensor))
    self.listen_state(self.motion_detected, entity=self.motion_sensor, new="on")



  def motion_detected (self, entity, attribute, old, new, kwargs):
    daylight_state = self.get_state(self.daylight_sensor)
    self.log("current daylight={}".format(daylight_state))
    if int(daylight_state) <=8:
      data="Motion detected in {}, turning on lights...".format(self.room)
      self.log(data)
      groupitem = self.get_state("group."+self.room,"all")
      lights = groupitem['attributes']['entity_id']
      for l in lights:
        if "light" in l or "lamp" in l:
          if self.get_state(l) != "on":
            self.log("turning {} on...".format(l))
            self.turn_on(l)
          else:
            self.log ("{} already on".format(l))

