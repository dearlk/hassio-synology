import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
from myglobals import logger as logger
import myglobals
#
# Tracker App
#
# Args:
# 

class TrackerNew(hass.Hass):

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
    
    # global flags
    self._last_location   = None
    self._left_home       = False
    self._left_work       = False
    self._reached_home    = False
    self._reached_work    = False


    for a in self.args:
      self.message="{}={}".format(a, self.args[a])
      logger(self)
    #self.listen_state(self.track, self.tracker)
    self.listen_state(self.reached_home, self.tracker,      old="not_home",    new="home")
    self.listen_state(self.left_home,    self.tracker,      old="home",        new="not_home")
    self.listen_state(self.reached_work, self.tracker,      old="not_home",    new=self.work_zone)
    self.listen_state(self.left_work,    self.tracker,      old=self.work_zone,new="not_home")
    #self.listen_state(self.left_work, self.tracker)

##############################################################################################
  def left_home (self, entity, attribute, old, new, kwargs):
    if self._left_home is False:
      self._left_home = True
      self._reached_home = False
      self.message = "{} has left home, tracking now...".format(self.pname)
      logger(self,flag=1)
      now = datetime.now()
      self.handler = self.run_every (self.track, now, int(float(self.get_state(self.interval))*60), left="home")


  def reached_home (self, entity, attribute, old, new, kwargs):
    if self._reached_home is False:
      self._reached_home = True
      self._left_home = False
      self.cancel_tracker()
      self.message = "{} has reached home just now".format(self.pname)
      logger(self,flag=1)


  def reached_work (self, entity, attribute, old, new, kwargs):
    if self._reached_work is False:
      self._reached_work = True
      self._left_work = False
      self.cancel_tracker()
      self.message = "{} has reached office now".format(self.pname)
      logger(self,flag=1)


  def left_work (self, entity, attribute, old, new, kwargs):
    if self._left_work is False:
      self._left_work = True
      self._reached_work = False
      self.message = "{} has left office, tracking now...".format(self.pname)
      logger(self,flag=1)
      now = datetime.now()
      self.handler = self.run_every (self.track, now, int(float(self.get_state(self.interval))*60), left="work")


  ############################################################################################
  def track (self, kwargs): 
   
    state = self.get_tracker_state(self.tracker)
    left = kwargs['left']
    
    if self.get_state(self.home_towards) == "on":
      to = "home"
    elif self.get_state(self.work_towards) == "on":
      to = "work"
    else:
      to = "somewhere"

    if state == "home":
      self.message ="looks like a false travel sensor activated, ignoring it"
      logger(self)  
      return

    if state == "home" and to == self.work_zone:
      self.message("false alarm... cancelling traker")
      logger(self)
      return

    location = self.get_state(self.geomap).split(",")[1]
    zone = self.get_tracker_state(self.tracker)
    #annouce zone name if available
    if zone != "not_home":
      location = zone

    # if not at home or office but not moving... e.g. last location == current location
    if self._last_location is None:
      self._last_location = location
    elif self._last_location == location:
      self.message ="looks like not moving at the moment..."
      logger(self,flag=1)
      self._last_location = location
      return
        
    distance_to_home = self.get_state(self.proximity_home)
    distance_to_work = self.get_state(self.proximity_work)
    time_to_home = self.get_state(self.time_to_home)
    time_to_work = self.get_state(self.time_to_work)
    
    if to == "home":
      self.message = "{} is traveling towards {}. Travel distance is {}km and estimated travel time {}min. {} has reached {} now".format(self.pname,to,distance_to_home,time_to_home,self.pname,location)
    elif to == "work":
      self.message = "{} is traveling towards {}. Travel distance is {}km and estimated travel time {}min. {} has reached {} now".format(self.pname,to,distance_to_work,time_to_work,self.pname,location)
    else:
      self.message = "{} is traveling {}. He has reached {} now".format(self.pname,to,location)
    
    logger(self,flag=1)

    if to == "home" and state == "home":
      self.message="reached home, cancelling the tracker now..."
      logger(self)
      self.cancel_tracker()
      self.message="done"
      logger(self)
      return

    if to == "work" and state == self.work_zone:
      self.message="reached work, cancelling the tracker now..."
      logger(self)
      self.cancel_tracker()  
      self.message="done"
      logger(self)
      return

################################################################################################################
  def cancel_tracker (self): 
    try:
        self.cancel_timer(self.handler)
    except KeyError:
        self.message='Tried to cancel a timer for {}, but none existed!'.format(self.tracker)
        logger(self)


    
    