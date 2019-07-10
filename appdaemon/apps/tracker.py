import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
from myglobals import logger as logger
import myglobals
#
# Tracker App
#
# Args:
# 

class Tracker(hass.Hass):

  def initialize(self):
    self.handler          = None
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
    
    

    for a in self.args:
      self.message="{}={}".format(a, self.args[a])
      logger(self)

    self.listen_state(self.reached_home, self.tracker,      old="not_home",    new="home")
    self.listen_state(self.left_home,    self.tracker,      old="home",        new="not_home")
    self.listen_state(self.reached_work, self.tracker,      old="not_home",    new=self.work_zone)
    self.listen_state(self.left_work,    self.tracker,      old=self.work_zone,new="not_home")
    self.listen_state(self.track,        self.home_towards, old="off",         new="on",          to="home")
    self.listen_state(self.track,        self.work_towards, old="off",         new="on",          to="work")
    
    self.listen_state(self.zone_tracker, self.tracker)

    self.message = "{} is currently at {} ".format(self.tracker,self.get_tracker_state(self.tracker))
    logger (self)
    

##############################################################################################
# zone_tracker
##############################################################################################
  def zone_tracker (self, entity, attribute, old, new, kwargs): 
    if old != new and new != "not_home":
      self.message = "{} have reached {}".format(self.pname,self.get_tracker_state(self.tracker))
      logger (self,flag=1)

  def reached_home (self, entity, attribute, old, new, kwargs):
    self.message = "{} has reached home just now".format(self.pname)
    logger(self,flag=1)


  def reached_work (self, entity, attribute, old, new, kwargs):
    self.message = "{} has reached office now".format(self.pname)
    logger(self,flag=1)


  def left_home (self, entity, attribute, old, new, kwargs):
    self.message = "{} has left home, tracking now".format(self.pname)
    logger(self,flag=1)

  def left_work (self, entity, attribute, old, new, kwargs):
    self.message = "{} has left office, tracking now".format(self.pname)
    logger(self,flag=1)


  def track (self, entity, attribute, old, new, kwargs): 
    self.message = "travel sensor activated"
    logger(self,flag=1)
    self.message="cancelling old tracker..."
    logger(self,flag=1)
    self.cancel_tracker()
    self.message="done"
    logger(self,flag=1)
    
    state = self.get_tracker_state(self.tracker)
    to = kwargs['to']

    if ( state == "home" and to == "work") or ( state == self.work_zone and to =="home"):
      self.message ="looks like a false travel sensor activated, ignoring it"
      logger(self,flag=1)  
      return

    now = datetime.now()
    self.handler = self.run_every(self.notify_travel, now, int(self.get_state(self.interval)) * 60, to=to)



  def notify_travel (self, kwargs):
    to = kwargs['to']
    state = self.get_tracker_state(self.tracker)
    self.message = "to={} and state={}".format(to,state)
    logger(self,flag=1)

    if state == "home" and to == self.work_zone:
      self.message("false alarm... cancelling traker")
      logger(self,flag=1)
      self.cancel_tracker()  
      self.message="done"
      logger(self,flag=1)
      return

    if to == "home" and state == "home":
      self.message="reached home, cancelling the tracker now..."
      logger(self,flag=1)
      self.cancel_tracker()
      self.message="done"
      logger(self,flag=1)
      return
    if to == "work" and state == self.work_zone:
      self.message="reached work, cancelling the tracker now..."
      logger(self,flag=1)
      self.cancel_tracker()  
      self.message="done"
      logger(self,flag=1)
      return




    location = self.get_state(self.geomap).split(",")[1]
    zone = self.get_tracker_state(self.tracker)
    #annouce zone name if available
    if zone != "not_home":
      location = zone

    distance_to_home = self.get_state(self.proximity_home)
    time_to_home = self.get_state(self.time_to_home)
    time_to_work = self.get_state(self.time_to_work)
    distance_to_work = self.get_state(self.proximity_work)
    
    if to == "home":
      self.message = "{} is traveling towards {}. \
      Travel distance is {}km and estimated travel time {}min. \
      {} has reached {} now".format(self.pname,to,distance_to_home,time_to_home,self.pname,location)
    elif to == "work":
      self.message = "{} is traveling towards {}. \
      Travel distance is {}km and estimated travel time {}min. \
      {} has reached {} now".format(self.pname,to,distance_to_work,time_to_work,self.pname,location)
    else:
      self.message = "{} is traveling somewhere. He has reached {} now".format(self.pname,location)
    
    logger(self,flag=1)
    #self.notify (self.message,name=myglobals.notify)
      

  def cancel_tracker (self): 
    try:
        self.cancel_timer(self.handler)
    except KeyError:
        self.message='Tried to cancel a timer for {}, but none existed!'.format(self.tracker)
        logger(self,flag=1)


    
    