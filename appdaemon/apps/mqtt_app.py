import appdaemon.plugins.hass.hassapi as hass
import appdaemon.plugins.mqtt.mqttapi as mqtt
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
import json
# MQTTApp App
#
# Args:
#

class MQTTApp(hass.Hass):

  def initialize(self):
    self.prefix = self.args.get("name")
    self.sensor_name = "mobile_in_use"
    self.locations = {}
    self.log("monitoring MQTT messages for zanzito/{}...".format(self.prefix))
    self.set_namespace("mqtt")
    #self.listen_event(self.mqtt_message_received, "MQTT_MESSAGE", topic = 'zanzito/{}/samsung_pick_up_gesture'.format(self.prefix))
    #self.listen_event(self.mqtt_message_received, "MQTT_MESSAGE", topic = 'zanzito/{}/motion_sensor'.format(self.prefix))
    #self.listen_event(self.mqtt_message_received, "MQTT_MESSAGE", topic = 'zanzito/{}/samsung_significant_motion_sensor'.format(self.prefix))
    #self.listen_event(self.mqtt_message_received, "MQTT_MESSAGE", topic = 'zanzito/{}/screen_orientation_sensor'.format(self.prefix))
    self.listen_event(self.device_info_received, "MQTT_MESSAGE", topic = 'zanzito/{}/device_info'.format(self.prefix))
    self.listen_event(self.find3_learn_received, "MQTT_MESSAGE", topic = 'myhome/learn/{}/office'.format(self.prefix))
    self.listen_event(self.find3_learn_received, "MQTT_MESSAGE", topic = 'myhome/learn/{}/bedroom'.format(self.prefix))
    self.listen_event(self.find3_learn_received, "MQTT_MESSAGE", topic = 'myhome/learn/{}/livingroom'.format(self.prefix))
    self.listen_event(self.find3_track_received, "MQTT_MESSAGE", topic = 'myhome/track/{}'.format(self.prefix))
    #self.run_every(self.update_sensor, datetime.now(), 1 * 60)
  
  # def mqtt_message_received(self, event_name, data, kwargs):
  #   topic = data['topic']
  #   self.log(topic)
  #   #payload = data['payload']
  #   #self.log(payload)
  #   #sensor_name = topic.split("/")[2]
    
  #   n = datetime.now()
  #   t = n.strftime("%H:%M:%S")
  #   if "screen_orientation_sensor" in topic:
  #     payload = data['payload']
  #     if payload=='':
  #       return
  #     else:
  #       payload = json.loads(data['payload'])
      
  #     orientation = payload.get('value0')
  #     #self.log(orientation)
  #     if orientation != -1:
  #       #self.log("orientation is {}, updating..".format(orientation))
  #       self.set_state("sensor.{}_{}".format(self.prefix,self.sensor_name),state=t,namespace="default")
  #       self.set_state("binary_sensor.{}_sleeping".format(self.prefix),state="off",namespace="default")
  #     #else:
  #       #self.log("orientation is {}, ignoring as phone at rest..".format(orientation))
  #   else:
  #     self.set_state("sensor.{}_{}".format(self.prefix,self.sensor_name),state=t,namespace="default")
  #     self.set_state("binary_sensor.{}_sleeping".format(self.prefix),state="off",namespace="default")

  def device_info_received(self, event_name, data, kwargs):
    topic = data['topic']
    payload = json.loads(data['payload'])
    screen_locked = payload.get('screen_locked')
    #self.log("topic={},payload={},screen_locked={}".format(topic,payload,screen_locked)) 
    if screen_locked is not None:
      if screen_locked is True:
        state_value="on"
      else:
        state_value="off"
      self.set_state("binary_sensor.{}_phone_screen_locked".format(self.prefix),state=state_value,namespace="default")

  def find3_learn_received(self, event_name, data, kwargs):
    topic = data['topic']
    location = topic.split("/")[3]
    location_data = data['payload']
    #self.log("topic={},location={},location_data={}".format(topic,location,location_data))
    #self.log("setting up room location data sensor now....") 
    #self.set_state("sensor.{}_{}_location".format(self.prefix,location),state=location_data,namespace="default")
    self.locations[location] = location_data

  def find3_track_received(self, event_name, data, kwargs):
    topic = data['topic']
    data = data['payload']
    #self.log("topic={},data={}".format(topic,data)) 
    for room in ["bedroom", "office", "livingroom"]:
      if room in self.locations:
        if data == self.locations[room]:
          self.set_state("sensor.{}_room_location".format(self.prefix),state=room,namespace="default")
          break

    #self.log("topic={},location={},location_data={}".format(topic,location,location_data)) 
    


  # def update_sensor(self,kwargs):
  #   self.set_namespace("default")
  #   sensor_name = "mobile_in_use"
  #   entity = "sensor.{}_{}".format(self.prefix,sensor_name)
  #   if self.entity_exists(entity):
  #     l = self.get_state(entity)
  #   else: 
  #     return
  #   n = datetime.now()
  #   n_s = str(n.hour) + ":" + str(n.minute) + ":" + str(n.second)
  #   FMT="%H:%M:%S"
  #   tdelta = datetime.strptime(n_s, FMT) - datetime.strptime(l, FMT)
  #   #self.log ("time since last mqtt message...{} seconds".format(tdelta.seconds))
  #   bed_time = self.get_state("input_datetime.bed_time")
  #   morning_alarm_time = self.get_state("input_datetime.morning_alarm_time")
  #   if self.now_is_between (bed_time,morning_alarm_time):
  #     if tdelta.seconds >= 30*60:
  #       #self.log("updating sleep sensor to on...")
  #       self.set_state("binary_sensor.{}_sleeping".format(self.prefix),state="on")
    
  #   # if tdelta.seconds >= 30*60:
  #   #   self.log("updating sleep sensor to on...")
  #   #   self.set_state("binary_sensor.{}_sleeping".format(self.prefix),state="on")
