import appdaemon.plugins.hass.hassapi as hass
import datetime
#import globals

#
# WorkdayAnnouncements App
#
# Args:
# None

class WorkdayAnnouncements(hass.Hass):

  def initialize(self):
    self.handler = None
    #self.announce_time()
    #if self.get_state("binary_sensor.workday") == "on":
    self.handler = self.run_every(self.announce_now, datetime.datetime.now(), 15 * 60)
    #else:
    #  self.handler = self.run_every(self.announce_time, datetime.datetime.now(), 15 * 60)

  def terminate (self):  
    self.cancel_timer(self.handler)

  def announce_now (self, kwargs):
    if self.get_state("binary_sensor.workday") == "off":
      return
      
    time = datetime.datetime.now().strftime('%I:%M')
    ctime = self.time()
    self.log(ctime)
    message = None

    #if self.now_is_between ("06:30:00","07:00:00"):
    #  message = "hello, good morning! it's {} now".format(time)
    #if self.now_is_between ("07:00:00","07:15:00"):
    #  message = "hello, just to let you know, it's {} now".format(time)
    #elif self.now_is_between ("07:15:00","07:30:00"):
    #  message = "Lalit please get up now, it's {} now".format(time)
    if self.now_is_between ("07:30:00","07:45:00"):
      if self.get_tracker_state("device_tracker.lalit") == "home":
        message = "Lalit, you will be late to office if you're still sleeping, it's {} now".format(time)
      else:
        message = time  

    elif self.now_is_between ("07:45:00","08:00:00"):
      message = "it's {} now".format(time)
    elif self.now_is_between ("08:00:00","08:15:00"):
      message = "it's {} now".format(time)
    elif self.now_is_between ("08:15:00","08:30:00"):
      if self.get_tracker_state("device_tracker.lalit") == "home":
        message = "Lalit, you should be leaving now, it's {} now".format(time)
      else:
        message = time  
    elif self.now_is_between ("08:30:00","08:45:00"):
      if self.get_tracker_state("device_tracker.lalit") == "home":
        message = "Lalit, you're late now, better take a cab! it's {} now".format(time)
      else:
        message = time  
    elif self.now_is_between ("08:45:00","09:00:00"):
      if self.get_tracker_state("device_tracker.jyoti") == "home":
        message = "Jyoti, you better get up now, it's {} now".format(time)
      else:
        message=time  
    elif self.now_is_between ("09:00:00","10:30:00"):
      message = "it's {} now".format(time)
    else:
      message = time

    self.log("message={}".format(message))  
    self.set_state("sensor.appd_notify",state=message, attributes={"announce":True, "frontend":False})
    
  
    
  def announce_time (self):
    time = datetime.datetime.now().strftime('%I:%M')
    self.log("time={}".format(time)) 
    self.set_state("sensor.appd_notify",state=time, attributes={"announce":True, "frontend":False})
    
      