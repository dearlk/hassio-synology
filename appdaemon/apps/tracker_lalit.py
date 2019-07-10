import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
from datetime import time

#
# TrackerLalit App
#
# Args:
# 

class TrackerForLalit(hass.Hass):

  def initialize(self):
    
    self._handler         = None
    self.message          = None
    self.tracker          = self.args["tracker"]
    #self.home_tracker     = self.args["home_tracker"]
    self.is_at_home       = self.args["is_at_home"]
    self.geomap           = self.args["geomap"]
    self.proximity_home   = self.args["proximity_home"]
    self.proximity_work   = self.args["proximity_work"]
    self.home_towards     = self.args["home_towards"]
    self.work_towards     = self.args["work_towards"]
    self.time_to_home     = self.args["time_to_home"]
    self.time_to_work     = self.args["time_to_work"]
    self.pname            = self.args["name"]
    self.work_zone        = self.args["work_zone"]
    self.interval         = self.args["ttls"]
    # global flags
    self._last_location   = None
    
    self.log("##############################################################################################")
    for a in self.args:
      self.message="{}={}={}".format(a, self.args[a], self.get_state(self.args[a]))
      self.log(self.message)
    self.log("##############################################################################################")
    self.listen_state(self.left_home,    self.tracker, old="home",         new="not_home",     duration=60)
    self.listen_state(self.reached_home, self.tracker, old="not_home",     new="home",         duration=60)
    self.listen_state(self.left_work,    self.tracker, old=self.work_zone, new="not_home",     duration=60)
    self.listen_state(self.reached_work, self.tracker, old="not_home",     new=self.work_zone, duration=60)
    self.listen_state(self.track_state_change, self.tracker)
    self.run_daily(self.reset, time(0,0,0))

#####################################################################################################################################
  def terminate (self):  
    #self.reset()
    #self.cancel_tracker()
    #if self._handler != None:
    self.cancel_timer(self._handler)
#####################################################################################################################################
  def reset (self, kwargs):  
    #if self.everyone_home():
    self.message='resetting all flags and sensors now...'
    self.log(self.message)
    self.cancel_timer(self._handler)
#####################################################################################################################################
  def track_state_change (self, entity, attribute, old, new, kwargs): 
    if old != new and new != "not_home" and new != "home":
      if self.get_state(self.tracker) != "home":
        self.message = "{} has reached {} now".format(self.pname, new)
        self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True})
#####################################################################################################################################
  def left_home (self, entity, attribute, old, new, kwargs): 
    #if self.get_state(self.is_at_home) == "on":
    #  return
    self.log("left_home->old={},new={}".format(old,new))
    self.set_state("sensor." + self.pname + "_left_home",state=self.time().strftime('%H:%M'))
    self.message = "{} has left home".format(self.pname)
    self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True, "frontend":False})
    self._ttls = int(float(self.get_state(self.interval))*60)
    if self._handler != None:
      self.cancel_timer(self._handler)
    self._handler = self.run_every (self.notify_travel, datetime.now(), self._ttls)
#####################################################################################################################################
  def reached_home (self, entity, attribute, old, new, kwargs): 
    #if self.get_state(self.is_at_home) == "off":
    #  return    
    self.log("reached_home->old={},new={}".format(old,new))
    self.set_state("sensor." + self.pname + "_reached_home",state=self.time().strftime('%H:%M'))
    self.message = "{} has reached home".format(self.pname)
    self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True, "frontend":False})
    #self.reset()
    if self._handler != None:
      self.cancel_timer(self._handler)
    #self.cancel_tracker()
#####################################################################################################################################
  def left_work (self, entity, attribute, old, new, kwargs): 
    self.log("left_work->old={},new={}".format(old,new))
    self.set_state("sensor." + self.pname + "_left_work",state=self.time().strftime('%H:%M'))
    self.message = "{} has left work".format(self.pname)
    self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True})
    self._ttls = int(float(self.get_state(self.interval))*60)
    if self._handler != None:
      self.cancel_timer(self._handler)
    self._handler = self.run_every (self.notify_travel, datetime.now(), self._ttls)
#####################################################################################################################################
  def reached_work (self, entity, attribute, old, new, kwargs): 
    self.log("reached_work->old={},new={}".format(old,new))
    self.set_state("sensor." + self.pname + "_reached_work",state=self.time().strftime('%H:%M'))
    self.message = "{} has reached work".format(self.pname)
    self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True})
    #self.reset()
    if self._handler != None:
      self.cancel_timer(self._handler)
    #self.cancel_tracker()
#####################################################################################################################################
  def notify_travel (self, kwargs):
    location = self.get_state(self.geomap).split(",")[1]
    zone = self.get_tracker_state(self.tracker)
    if zone == "home" or zone == self.work_zone:
      return
    if (zone != "not_home" and zone != self.work_zone) and location != self._last_location:
      location = zone
      self.message = "{} has reached {} now".format(self.pname,location)
      self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True, "frontend":False})
      self._last_location = location
#####################################################################################################################################      
  def cancel_tracker (self): 
    try:
        self.message="cancelling {} now".format(self._handler)
        self.log(self.message)
        self.cancel_timer(self._handler)
        self._handler=None
    except KeyError:
        self.message='Tried to cancel a timer for {}, but none existed!'.format(self._handler)
        self.log(self.message)
