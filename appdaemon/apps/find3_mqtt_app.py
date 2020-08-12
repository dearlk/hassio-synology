import appdaemon.plugins.hass.hassapi as hass
import appdaemon.plugins.mqtt.mqttapi as mqtt
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

# MQTTApp App
#
# Args:
#

class FIND3MQTTApp(hass.Hass):

  def initialize(self):
    self.last_probability=0
    self.new_probability=0
    self.last_room=None
    self.new_room=None
    self.pass_counter=0
    self.prefix = self.args.get("name")
    self.log("monitoring MQTT messages for zanzito/{}...".format(self.prefix))
    self.set_namespace("mqtt")
    #self.listen_event(self.device_info_received, "MQTT_MESSAGE", topic = 'zanzito/{}/device_info'.format(self.prefix))
    self.listen_event(self.find3_mqtt_received, "MQTT_MESSAGE", topic = 'myhome/location/{}'.format(self.prefix))

# #############################################################  
#   def find3_mqtt_received(self, event_name, data, kwargs):
#     #self.log("find3_mqtt_received") 
#     self.log("++++++++++++++++++++") 
#     #self.log("                   ") 
#     #self.log(data)
#     topic = data['topic']
#     payload = json.loads(data['payload'])
#     guesses = payload.get("guesses")
#     self.log(guesses)
#     self.last_probability=0
#     #room=None
#     for guess in guesses:
#       if "probability" in guess:
#         self.new_probability = float(guess["probability"])
#         #self.log("probability={}".format(probability))
#         if self.new_probability > self.last_probability:
#           self.last_probability = self.new_probability
#           self.new_room = guess["location"]
#           #self.log("room={},probability={}".format(self.new_room,self.new_probability))
#     new_room_motion = self.get_state("binary_sensor.{}_motion".format(self.new_room),namespace="default")
#     seconds_since_last_steps_updated = self.get_state("sensor.{}_seconds_since_last_steps_updated".format(self.prefix),namespace="default")
#     #self.log("new_room_motion={}".format(new_room_motion))
#     #self.log("seconds_since_last_steps_updated={}".format(seconds_since_last_steps_updated))
#     if self.last_room is None:
#       self.set_state("sensor.{}_room_location".format(self.prefix),state=self.new_room,namespace="default")
#       self.set_state("sensor.{}_last_room_location".format(self.prefix),state=self.last_room,namespace="default")
#       self.last_room=self.new_room
#     elif self.last_room != self.new_room and new_room_motion=="on" and (self.last_room is None or seconds_since_last_steps_updated is None or int(seconds_since_last_steps_updated) <=300):
#       self.log("last_room({})<>new_room({}) and new room motion={} and seconds_since_last_steps_updated={} hence updating...".format(self.last_room,self.new_room,new_room_motion,seconds_since_last_steps_updated))
#       self.set_state("sensor.{}_room_location".format(self.prefix),state=self.new_room,namespace="default")
#       self.set_state("sensor.{}_last_room_location".format(self.prefix),state=self.last_room,namespace="default")
#       self.last_room=self.new_room
#     else:
#       self.log("last_room({})=new_room({}) and new room motion={} and seconds_since_last_steps_updated={}  hence ignoring...".format(self.last_room,self.new_room,new_room_motion,seconds_since_last_steps_updated))


#     #self.log("                   ") 
#     #self.log("++++++++++++++++++++")
#     #self.sleep(60)

#############################################################  
  def find3_mqtt_received(self, event_name, data, kwargs):
    #self.log("++++++++++++++++++++") 
    #self.log(data)
    topic = data['topic']
    payload = json.loads(data['payload'])
    guesses = payload.get("guesses")
    #self.log(guesses)
    self.last_probability=0
    for guess in guesses:
      if "probability" in guess:
        self.new_probability = float(guess["probability"])
        if self.new_probability > self.last_probability:
          self.last_probability = self.new_probability
          self.new_room = guess["location"]
          if self.last_room != self.new_room and self.pass_counter >=2:
            self.pass_counter=0
            self.set_state("sensor.{}_room_location".format(self.prefix),state=self.new_room,namespace="default")
            self.set_state("sensor.{}_last_room_location".format(self.prefix),state=self.last_room,namespace="default")
            self.last_room=self.new_room
          else:
            self.pass_counter=self.pass_counter+1  
    #self.log("++++++++++++++++++++") 