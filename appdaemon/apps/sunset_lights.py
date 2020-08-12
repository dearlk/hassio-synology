import appdaemon.plugins.hass.hassapi as hass
import datetime
#import globals

#
# SunsetLights App
#
# Args:
# sunset_lights: name of light, switch or group to be turned on at sunset

class SunsetLights(hass.Hass):

  def initialize(self):

    runtime = datetime.time(00,00,00)
    self.run_at_sunset(self.sunset_lights_turn_on,offset=-30*60)
    self.run_daily(self.sunset_lights_turn_off,runtime)
    self.listen_state(self.someone_at_home_now, "group.all_devices", new="home") 
    

  def sunset_lights_turn_on (self, kwargs):
    if self.anyone_home():
      #self.set_state("sensor.appd_notify",state="turning on sunset lights...", attributes={"announce":True, "frontend":True})
      self.turn_on(self.args["sunset_lights"])
      self.set_state("sensor.sunset_lights", state="on")

  def sunset_lights_turn_off (self, kwargs):
    #if self.get_state("binary_sensor.sleep_mode")=="on":
    #self.set_state("sensor.appd_notify",state="turning off sunset lights...", attributes={"announce":True, "frontend":True})
    self.turn_off(self.args["sunset_lights"])
    self.set_state("sensor.sunset_lights", state="off")

  def someone_at_home_now (self, entity, attribute, old, new, kwargs):
    if self.sun_down():
      if self.get_state(self.args["sunset_lights"])=="off" and self.get_state("binary_sensor.sleep_mode")=="off":
        #self.set_state("sensor.appd_notify",state="Looks like someone just reached home, turning on the sunset lights now", attributes={"announce":True, "frontend":True})
        self.turn_on(self.args["sunset_lights"])
        self.set_state("sensor.sunset_lights", state=datetime.datetime.now().strftime('%I:%M'))



