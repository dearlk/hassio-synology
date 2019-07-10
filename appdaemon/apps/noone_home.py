import appdaemon.plugins.hass.hassapi as hass
#from datetime import datetime
#import globals
#
# NooneHome App
#
# Args:
# 

class NooneHome(hass.Hass):

  def initialize(self):
    self.listen_state(self.shutdown_everything, "group.all_devices", new="not_home", duration=5*60) 


  def shutdown_everything (self, entity, attribute, old, new, kwargs):
    self.log("no one at home, shuting down everything")
    self.set_state("sensor.appd_notify",state="Looks like no one at home, shutting down everything...", attributes={"announce":False, "frontend":True})
    self.call_service("homeassistant/turn_on", entity_id="script.shutdown_everything")
    #self.call_service("homeassistant/turn_off",entity_id="input_boolean.announcement_mode")
      
    



