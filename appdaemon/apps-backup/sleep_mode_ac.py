import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Sleep Mode App
#
# Args:
# 

class SleepModeAC(hass.Hass):

  def initialize(self):
    self.listen_state(self.sleep_mode_on, "binary_sensor.sleep_mode")

  def sleep_mode_on (self, entity, attribute, old, new, kwargs):
    if new=="off":
      self.turn_off("switch.office_aircon")
      return
    self.run_every(self.change_temp, datetime.datetime.now(), 60 * 60)

  def change_temp (self,kwargs):
    if self.get_state("device_tracker.lalit")=="home":
      if self.now_is_between ("22:00:00","00:00:00"):
        self.log("setting temperature to 18c")
        self.call_service("climate/set_temperature", entity_id="climate.office_aircon", temperature="18", operation_mode="cool")  
      elif self.now_is_between ("00:00:00","02:00:00"):
        self.log("setting temperature to 24c")
        self.call_service("climate/set_temperature", entity_id="climate.office_aircon", temperature="24", operation_mode="cool")
      elif self.now_is_between ("02:00:00","04:00:00"):
        self.log("setting temperature to 26c")
        self.call_service("climate/set_temperature", entity_id="climate.office_aircon", temperature="26", operation_mode="cool")
      elif self.now_is_between ("05:00:00","06:00:00"):
        self.turn_off("switch.office_aircon")
      
