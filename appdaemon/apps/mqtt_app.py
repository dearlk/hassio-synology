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
    self.last_probability=0
    self.new_probability=0
    self.last_room=None
    self.new_room=None

    self.prefix = self.args.get("name")
    self.log("monitoring MQTT messages for zanzito/{}...".format(self.prefix))
    self.set_namespace("mqtt")
    self.listen_event(self.device_info_received, "MQTT_MESSAGE", topic = 'zanzito/{}/device_info'.format(self.prefix))
    #self.listen_event(self.find3_mqtt_received, "MQTT_MESSAGE", topic = 'myhome/location/{}'.format(self.prefix))
    
#############################################################################################################################
  def device_info_received(self, event_name, data, kwargs):
    topic = data['topic']
    payload = json.loads(data['payload'])
    screen_locked = payload.get('screen_locked')
    mobile_charging = payload.get('battery_charging')
    mobile_charging_value=""
    screen_locked_value=""
    #self.log("topic={},payload={},screen_locked={},mobile_charging={}".format(topic,payload,screen_locked,mobile_charging)) 
    #self.log("device_info_received") 
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


