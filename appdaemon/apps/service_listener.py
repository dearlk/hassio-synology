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
    #self.listen_event(self.callb, event="call_service", domain="automation")
    self.listen_event(self.callb, event="call_service", domain="script")
    self.listen_event(self.callb, event="call_service", domain="media_player")
        

  def callb(self, event_name, data, kwargs):
    self.log("event_name={}, data={}".format(event_name,data))
    self.notify("data={}".format(data), title="appdaemon service listener", name=myglobals.notify_service)




