import appdaemon.plugins.hass.hassapi as hass
#import datetime
#import globals

#
# GallaryLight App
#
# Args:
# light: name of light, switch or group to be turned on using door sensors

class GallaryLight(hass.Hass):

  def initialize(self):
    self.sensor = self.args["sensor"]
    self.light = self.args["light"]
    self.door = self.args["door"]

    self.log("##############################################################################################")
    for a in self.args:
      self.log("{}={}={}".format(a, self.args[a], self.get_state(self.args[a])))
    self.log("##############################################################################################")

    self.listen_state(self.turn_on_light, self.sensor, new="on") 
    self.listen_state(self.turn_off_light, self.sensor, new="off") 


  def turn_on_light (self, entity, attribute, old, new, kwargs):
    self.log("turning light on...")
    self.turn_on(self.light)
    self.set_state("sensor.gallary_light_last_door", state=self.door)

  def turn_off_light (self, entity, attribute, old, new, kwargs):
    if self.get_state("sensor.gallary_light_last_door") == self.door:
      self.log("turning light off...")
      self.turn_off(self.light)
      self.set_state("sensor.gallary_light_last_door", state="")

  