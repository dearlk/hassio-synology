import appdaemon.plugins.hass.hassapi as hass
import myglobals
import datetime

# ServiceListener App
#
# Args:
#

class ServiceListener(hass.Hass):

  def initialize(self):
    self.log("Initializing...")
    self.listen_event(self.callb, event="call_service", domain="automation")
    self.listen_event(self.callb, event="call_service", domain="script")
    #self.listen_event(self.callb, event="call_service", domain="media_player")
    #self.listen_event(self.callb, event="call_service", domain="switch")
    #self.listen_event(self.callb, event="call_service", domain="input_boolean")
    #self.listen_event(self.callb, event="call_service")

  def callb(self, event_name, data, kwargs):
    self.log("event_name={}, data={}".format(event_name,data))
    #self.notify("service={},service_data={}".format(data.service,data.service_data), name=myglobals.notify_service)
    self.notify("{}".format(data), name=myglobals.notify_service)




