import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
from datetime import time

#
# Tracker3 App
#
# Args:
# 

class Tracker3(hass.Hass):

  def initialize(self):
    
    self.handler                      = None
    self._traveling_home_handler      = None
    self._traveling_work_handler      = None
    self._traveling_somewhere_handler = None

    self.message          = None
    self.tracker          = self.args["tracker"]
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
    self._last_location       = None
    self._prev_distance       = 0
    self._left_home           = False
    self._left_work           = False
    self._reached_home        = False
    self._reached_work        = False
    self._traveling_home_flag   = False
    self._traveling_work_flag   = False
    self._traveling_somewhere_flag = False
    self._ttls = int(float(self.get_state(self.interval))*60)
    
    self.log("##############################################################################################")
    for a in self.args:
      self.message="{}={}={}".format(a, self.args[a], self.get_state(self.args[a]))
      self.log(self.message)
    self.log("##############################################################################################")
    
    self.listen_state(self.left_home,    self.tracker, old="home",         new="not_home",     duration=60)
    self.listen_state(self.reached_home, self.tracker, old="not_home",     new="home",         duration=60)
    self.listen_state(self.left_work,    self.tracker, old=self.work_zone, new="not_home",     duration=0)
    self.listen_state(self.reached_work, self.tracker, old="not_home",     new=self.work_zone, duration=0)
    self.listen_state(self.traveling_home,   self.home_towards,   old="off", new="on", duration=60)
    self.listen_state(self.traveling_work,   self.work_towards,   old="off", new="on", duration=60)
    #self.listen_state(self.traveling_somewhere, self.proximity_home, old=0)
    self.listen_state(self.track_state_change, self.tracker)
    self.run_daily(self.reset, time(0,0,0))
    

#####################################################################################################################################
  def terminate (self):  
    self.reset(None)

#####################################################################################################################################
  def reset (self,kwargs):  
    if self.everyone_home():
      self.message='resetting all flags and sensors now...'
      self.log(self.message)
      
      self.set_state(self.home_towards,state="off")
      self.set_state(self.work_towards,state="off")
      self.set_state(self.proximity_home,state=0)
      
      self._traveling_home_flag=False
      self._traveling_work_flag=False
      self._traveling_somewhere_flag=False

      self.cancel_tracker(self._traveling_home_handler)
      self.cancel_tracker(self._traveling_work_handler)
      self.cancel_tracker(self._traveling_somewhere_handler)


#####################################################################################################################################
  def track_state_change (self, entity, attribute, old, new, kwargs): 
    if old != new and new != "not_home":
      self.message = "{} has reached {} now".format(self.pname, new)
      self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True})
      
  
#####################################################################################################################################
  def left_home (self, entity, attribute, old, new, kwargs): 
    self.log("left_home->old={},new={}".format(old,new))
    self.set_state("sensor." + self.pname + "_left_home",state=self.time().strftime('%H:%M'))
    self.message = "{} has left home".format(self.pname)
    self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True})
    
#####################################################################################################################################
  def reached_home (self, entity, attribute, old, new, kwargs): 
    self.log("reached_home->old={},new={}".format(old,new))
    self.set_state("sensor." + self.pname + "_reached_home",state=self.time().strftime('%H:%M'))
    self.message = "{} has reached home".format(self.pname)
    self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True})
    self._traveling_home_flag = False
    self._prev_distance=0
    self.reset(None)

#####################################################################################################################################
  def left_work (self, entity, attribute, old, new, kwargs): 
    self.log("left_work->old={},new={}".format(old,new))
    self.set_state("sensor." + self.pname + "_left_work",state=self.time().strftime('%H:%M'))
    self.message = "{} has left work".format(self.pname)
    self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True})
    
#####################################################################################################################################
  def reached_work (self, entity, attribute, old, new, kwargs): 
    self.log("reached_work->old={},new={}".format(old,new))
    self.set_state("sensor." + self.pname + "_reached_work",state=self.time().strftime('%H:%M'))
    self.message = "{} has reached work".format(self.pname)
    self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True})
    self._traveling_work_flag = False
    self._prev_distance=0
    self.reset(None)

#####################################################################################################################################
  def traveling_home (self, entity, attribute, old, new, kwargs):
    state = self.get_tracker_state(self.tracker)
    if state == "home":
      self.log("false alarm of traveling home_towards, returning now")
      return

    if self._traveling_home_handler is None and self._traveling_work_flag is False:
      self._traveling_home_flag = True
      self._traveling_home_handler = self.run_every (self.notify_travel_home, datetime.now(), self._ttls)


#####################################################################################################################################
  def traveling_work (self, entity, attribute, old, new, kwargs):
    state = self.get_tracker_state(self.tracker)
    if state == "home":
      self.log("false alarm of traveling work_towards, returning now")
      return
    if self.sun_down() or self.get_state("binary_sensor.workday") == 'off':
      self.log("false alarm of traveling work_towards, returning now")
      return
    if self._traveling_work_handler is None and self._traveling_home_flag is False:
      self._traveling_work_flag = True
      self._traveling_work_handler = self.run_every (self.notify_travel_work, datetime.now(), self._ttls)


#####################################################################################################################################
  def traveling_somewhere (self, entity, attribute, old, new, kwargs):
    if self._traveling_somewhere_handler is None and self._traveling_home_flag is False and self._traveling_work_flag is False:
      self._traveling_somewhere_flag = True
      self._traveling_somewhere_handler = self.run_every (self.notify_travel_somewhere, datetime.now(), self._ttls)


#####################################################################################################################################
  def notify_travel_home (self, kwargs):
    state = self.get_tracker_state(self.tracker)
    to = "home"
    if state == "home":
      self.cancel_tracker(self._traveling_home_handler);
      return

    location = self.get_state(self.geomap).split(",")[1]
    zone = self.get_tracker_state(self.tracker)
    if zone != "not_home":
      location = zone

    if location != self._last_location:
      # distance_to_home = self.get_state(self.proximity_home)
      # if self._prev_distance == 0:
      #   time_to_home = self.get_state(self.time_to_home)
      #   self._prev_distance = distance_to_home
      # else:
      #   time_to_home = self.calculate_time(self._prev_distance, distance_to_home, self._ttls)
      distance_to_home = self.get_state(self.proximity_home)
      time_to_home = self.get_state(self.time_to_home)
      self.message = "{} is traveling {}. Estimated distance & time is {}km and {}min. {} has reached {} now".format(self.pname,to,distance_to_home,time_to_home,self.pname,location)
      self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True, "frontend":False})
      
      self._last_location = location

#####################################################################################################################################
  def notify_travel_work (self, kwargs):
    state = self.get_tracker_state(self.tracker)
    to = "work"
    if state == self.work_zone:
      self.cancel_tracker(self._traveling_work_handler);
      return

    location = self.get_state(self.geomap).split(",")[1]
    zone = self.get_tracker_state(self.tracker)
    if zone != "not_home":
      location = zone

    if location != self._last_location:
    #   distance_to_work = self.get_state(self.proximity_work)
    #   if self._prev_distance == 0:
    #     time_to_work = self.get_state(self.time_to_work)
    #     self._prev_distance = distance_to_work
    #   else:
    #     time_to_work = self.calculate_time(self._prev_distance, distance_to_work, self._ttls)
      distance_to_work =  self.get_state(self.proximity_work)
      time_to_work =  self.get_state(self.time_to_work)
      self.message = "{} is traveling {}. Estimated distance & time is {}km and {}min. {} has reached {} now".format(self.pname,to,distance_to_work,time_to_work,self.pname,location)
      self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True, "frontend":False})
      
      self._last_location = location

      
#####################################################################################################################################
  def notify_travel_somewhere (self, kwargs):
    state = self.get_tracker_state(self.tracker)
    to = "somewhere"
    if state == self.work_zone:
      self.cancel_tracker(self._traveling_somewhere_handler);
      return

    location = self.get_state(self.geomap).split(",")[1]
    zone = self.get_tracker_state(self.tracker)
    if zone != "not_home":
      location = zone

    if location != self._last_location:
      self.message = "{} is traveling {}. {} has reached {} now".format(self.pname,to,self.pname,location)
      self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True, "frontend":False})
      
      self._last_location = location

#####################################################################################################################################      
  def cancel_tracker (self, handler): 
    try:
        self.message="cancelling {} now".format(handler)
        self.log(self.message)
        self.cancel_timer(handler)
        handler=None
    except KeyError:
        self.message='Tried to cancel a timer for {}, but none existed!'.format(handler)
        self.log(self.message)


#####################################################################################################################################      
  def calculate_time (self, prev_distance, curr_distance, ttls): 
    distance_covered = float(prev_distance) - float(curr_distance)
    self.log("distance_covered={}".format(distance_covered))
    time_taken = float(ttls/60)
    self.log("time_taken={}".format(time_taken))
    speed = float(distance_covered) / float(time_taken)
    #avoid divided by zero error
    if speed == 0:
      speed=.01
    self.log("speed={}".format(speed))
    time_left = float(curr_distance) / float(speed)
    self.log("time_left={}".format(time_left))
    return int(time_left)



