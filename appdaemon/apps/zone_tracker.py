import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
from globals import logger
#
# Tracker App
#
# Args:
# 

class ZoneTracker(hass.Hass):

  def initialize(self):
    self.message          = None
    self.tracker          = self.args["tracker"]
    self.listen_state(self.zone_tracker, self.tracker)
    self.globals = self.get_app('Globals')   
##############################################################################################
# zone_tracker
##############################################################################################
  def zone_tracker (self, entity, attribute, old, new, kwargs): 
    if old != new and new != "not_home":
      self.message = "You have reached {}".format(self.get_tracker_state(self.tracker))
      self.globals.logger (self.message,notify=1)