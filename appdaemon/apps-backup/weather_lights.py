import appdaemon.plugins.hass.hassapi as hass
import datetime
#import globals

#
# WeatherLights App
#
# Args:
# sunset_lights: name of light, switch or group to be turned on at sunset

class WeatherLights(hass.Hass):

  def initialize(self):
    self.listen_state(self.toggle_sunset_lights, "sensor.sunlight") 


  def toggle_sunset_lights (self, entity, attributes, old, new, kwargs):
    self.log("old={},new={}".format(old,new))
    if old == new:
      return
    if float(new) > 200 and float(new) < 800:
      return
       
    # it's day time  
    if self.now_is_between ("10:00:00","18:00:00"):
      state = self.get_state(self.args["sunset_lights"])
      if float(new) <= 200 and state == "off":
        self.set_state("sensor.appd_notify",state="Looks like it's dark outside, turning on sunset lights now...", attributes={"announce":True, "frontend":True})
        self.turn_on(self.args["sunset_lights"])
        self.set_state("sensor.sunset_lights", state="on")
      elif float(new) >= 800 and state == "on":
        self.set_state("sensor.appd_notify",state="Looks like it's bright outside, turning off sunset lights now...", attributes={"announce":True, "frontend":True})
        self.turn_off(self.args["sunset_lights"])
        self.set_state("sensor.sunset_lights", state="off")

  