import appdaemon.plugins.hass.hassapi as hass
import myglobals
#import date
import datetime
#import time
# Hellow World App
#
# Args:
#

class HelloWorld(hass.Hass):

  def initialize(self):
    self.log("HelloWorld from appdaemon!")
    #self.log(datetime.datetime.now().strftime('%I:%M'))
    #self.set_state("sensor.appd_notify",state="HelloWorld from appdaemon!")
    #self.set_state("sensor.appd_notify",state="Test8", attributes={"announce":True, "frontend":True})
    #self.call_service("group/set", add_entities="sensor.appd_notify")
    #self.listen_event(self.callb, event="call_service")
    self.listen_event(self.callb, event="call_service", domain="automation")
    self.listen_event(self.callb, event="call_service", domain="script")
    self.listen_event(self.callb, event="call_service", domain="switch")
    #self.call_service("homeassistant/turn_on",entity_id="input_boolean.announcement_mode")
    #self.call_service("tts/google_say",  entity_id="media_player.home", message="testing it now now")
        

  def callb(self, event_name, data, kwargs):
    self.log("event_name={}, data={}".format(event_name,data))
    self.notify("data={}".format(data), title="appdaemon service listener", name=myglobals.notify_service)




