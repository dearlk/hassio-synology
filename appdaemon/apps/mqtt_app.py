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

class MQTTApp(hass.Hass):

  def initialize(self):
    self.prefix = self.args.get("name")
    # self.data= self.args.get("data")
    # self.sensor_name = "mobile_in_use"
    # self.data_file = os.path.join(Path(__file__).parent.absolute(),self.data)
    # #load location data
    # if path.exists(self.data_file):
    #   self.log("loading locations data...")
    #   with open (self.data_file,"r") as f:
    #     self.locations = json.load(f)
    #     self.log(self.locations)
    # else:
    #     self.log("data file not found, setting dictionary...")
    #     self.locations = {"bedroom": [], "office": [], "livingroom": []}
    
    #self.log(self.locations)
    #self.locations = {"bedroom": {}, "office": {}, "livingroom": {}}

    self.log("monitoring MQTT messages for zanzito/{}...".format(self.prefix))
    self.set_namespace("mqtt")
    self.listen_event(self.device_info_received, "MQTT_MESSAGE", topic = 'zanzito/{}/device_info'.format(self.prefix))
    #self.listen_event(self.find3_learn_received, "MQTT_MESSAGE", topic = 'myhome/learn/{}/office'.format(self.prefix))
    #self.listen_event(self.find3_learn_received, "MQTT_MESSAGE", topic = 'myhome/learn/{}/bedroom'.format(self.prefix))
    #self.listen_event(self.find3_learn_received, "MQTT_MESSAGE", topic = 'myhome/learn/{}/livingroom'.format(self.prefix))
    #self.listen_event(self.find3_track_received, "MQTT_MESSAGE", topic = 'myhome/track/{}'.format(self.prefix))
    #self.listen_event(self.find_mqtt_received, "MQTT_MESSAGE", topic = 'myhome/location/{}'.format(self.prefix))
    self.listen_event(self.find3_mqtt_received, "MQTT_MESSAGE", topic = 'myhome/location/{}'.format(self.prefix))
    #self.listen_event(self.find3_mqtt_received, "MQTT_MESSAGE", topic = 'find3/location/{}'.format(self.prefix))
    self.listen_event(self.monitor_mqtt_received, "MQTT_MESSAGE", topic = 'monitor/office/{}'.format(self.prefix))

#############################################################################################################################
# save locations data
  # def terminate (self):
  #   with open(self.data_file,"w") as f:
  #     self.log("saving data...")
  #     json.dump(self.locations, f)
  #     self.log("done")

#############################################################################################################################
  def device_info_received(self, event_name, data, kwargs):
    topic = data['topic']
    payload = json.loads(data['payload'])
    screen_locked = payload.get('screen_locked')
    mobile_charging = payload.get('battery_charging')
    mobile_charging_value=""
    screen_locked_value=""
    self.log("topic={},payload={},screen_locked={},mobile_charging={}".format(topic,payload,screen_locked,mobile_charging)) 
    if screen_locked is not None:
      if screen_locked is True:
        screen_locked_value="on"
      else:
        screen_locked_value="off"
    if mobile_charging is not None:
      if mobile_charging is True:
        mobile_charging_value="on"
      else:
        mobile_charging_value="off"
    self.set_state("binary_sensor.{}_mobile_screen_locked".format(self.prefix),state=screen_locked_value,namespace="default")
    self.set_state("binary_sensor.{}_mobile_charging".format(self.prefix),state=mobile_charging_value,namespace="default")

#############################################################
  def find3_learn_received(self, event_name, data, kwargs):
    topic = data['topic']
    location = topic.split("/")[3]
    location_data = data['payload']
    self.log("topic={},location={},location_data={}".format(topic,location,location_data))
    if location_data not in (self.locations[location]):
      self.log("new datapoint found, recording now...")
      self.locations[location].append(location_data)
    else:
      self.log("datapoint ignored")
#############################################################  
  def find3_track_received(self, event_name, data, kwargs):
    topic = data['topic']
    data = data['payload']
    self.log("topic={},data={}".format(topic,data)) 
    for room in ["bedroom", "office", "livingroom"]:
      if room in self.locations:
        if data in self.locations[room]:
          self.set_state("sensor.{}_room_location".format(self.prefix),state=room,namespace="default")
          break

#############################################################  
  def find_mqtt_received(self, event_name, data, kwargs):
    topic = data['topic']
    payload = json.loads(data['payload'])
    room = payload.get("location")
    #self.log("topic={},data={}".format(topic,data)) 
    self.set_state("sensor.{}_room_location".format(self.prefix),state=room,namespace="default")


#############################################################  
  def find3_mqtt_received(self, event_name, data, kwargs):
    #self.log(data)
    topic = data['topic']
    payload = json.loads(data['payload'])
    guesses = payload.get("guesses")
    last_probability=0
    for guess in guesses:
      #self.log("guess={}".format(guess))
      probability = float(guess["probability"])
      if probability > last_probability:
        last_probability = probability
        room = guess["location"]
    #self.log("room={},probability={}".format(room,last_probability))
    #room = guesses[0]["location"]
    #self.log("topic={},data={},guesses={},room={}".format(topic,data,guesses, room)) 
    self.set_state("sensor.{}_room_location".format(self.prefix),state=room,namespace="default")

#############################################################  
  def monitor_mqtt_received(self, event_name, data, kwargs):
    self.log(data)
    topic = data['topic']
    payload = json.loads(data['payload'])
    confidence = payload.get("confidence")
    room = topic.split("/")[1]
    #room = guesses[0]["location"]
    self.set_state("sensor.{}_{}_monitor".format(self.prefix,room),state=confidence,namespace="default")
