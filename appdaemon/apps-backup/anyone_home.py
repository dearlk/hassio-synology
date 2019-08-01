import appdaemon.plugins.hass.hassapi as hass
#from datetime import datetime
#import globals
#
# AnyOneHome App
#
# Args:
# 

class AnyOneHome(hass.Hass):

  def initialize(self):
    self.listen_state(self.anyone_at_home, "group.all_devices", old="not_home", new="home", duration=0) 


  def anyone_at_home (self, entity, attribute, old, new, kwargs):
    sleep_mode = self.get_state("binary_sensor.sleep_mode")
    if sleep_mode is None:
      sleep_mode = 'off'
      
    if sleep_mode=="off":
      #self.set_state("sensor.appd_notify",state="Looks like someone just reached home, activating announcement mode...", attributes={"announce":True, "frontend":True})
      self.set_state("sensor.appd_notify",state="Looks like someone just reached home, activating announcement_mode...")
      self.call_service("homeassistant/turn_on",entity_id="input_boolean.announcement_mode")
    else:
      #self.set_state("sensor.appd_notify",state="Looks like someone just reached home but sleep mode is on so deactivating announcement_mode...", attributes={"announce":False, "frontend":True})
      self.set_state("sensor.appd_notify",state="Looks like someone just reached home but sleep mode is on so deactivating announcement_mode...")
      self.call_service("homeassistant/turn_off",entity_id="input_boolean.announcement_mode")
        
          
    




