import appdaemon.plugins.hass.hassapi as hass
import datetime
import myglobals

#
# WeatherLights App
#
# Args:
# sunset_lights: name of light, switch or group to be turned on at sunset

class WeatherLights(hass.Hass):

  def initialize(self):
    self.daylight_sensor = self.args["daylight_sensor"]
    self.listen_state(self.toggle_sunset_lights, self.daylight_sensor) 


  def toggle_sunset_lights (self, entity, attributes, old, new, kwargs):
    #self.log("old={},new={}".format(old,new))
    if old == new:
      return
    # it's day time  
    if self.now_is_between ("09:00:00","18:00:00"):
      slstate = self.get_state(self.args["sunset_lights"])
      self.log("checking sunset lights state={}".format(slstate))
      if int(new) <= 100 and slstate == "off":
        data= "Looks like it's dark outside, turning on sunset lights now..."
        #self.notify(data, name=myglobals.notify_service)
        self.turn_on(self.args["sunset_lights"])
        self.set_state("binary_sensor.sunset_lights", state="on")
        self.log(data)
        self.set_state("sensor.appd_notify",state=data, attributes={"announce":True, "frontend":True})
      elif int(new) >= 200 and slstate == "on":
        data= "Looks like it's bright outside, turning off sunset lights now..."
        #self.notify(data, name=myglobals.notify_service)
        self.turn_off(self.args["sunset_lights"])
        self.set_state("binary_sensor.sunset_lights", state="off")
        self.log(data)
        self.set_state("sensor.appd_notify",state=data, attributes={"announce":True, "frontend":True})

  