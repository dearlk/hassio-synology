import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Sleep Mode App
#
# Args:
# 

class SleepMode(hass.Hass):

  def initialize(self):
    self._auto = True
    #self.handler = self.run_every(self.sleep_mode, datetime.datetime.now(), 15 * 60)
    self.listen_state(self.sleep_mode_change, "input_boolean.sleep_mode")
    #self.run_daily(self.reset, datetime.time(12,0,0))
    self.run_daily(self.start_sleep_time, datetime.time(21,0,0))
    self.run_daily(self.end_sleep_time, datetime.time(9,0,0))


  def reset(self, kwargs):
    if not self._auto:
      self._auto = True

  def start_sleep_time(self, kwargs):
    self.log("setting sleep mode on")
    self.set_state("binary_sensor.sleep_mode", state="on")
    self.set_state("binary_sensor.announcement_mode", state="off")

  def end_sleep_time(self, kwargs):
    self.log("setting sleep mode off")
    self.set_state("binary_sensor.sleep_mode", state="off")
    self.set_state("binary_sensor.announcement_mode", state="on")

  # def terminate (self):  
  #   pass


  def sleep_mode (self, kwargs):
    if self._auto:
      workday = self.get_state("binary_sensor.workday")
      tv = self.get_state("binary_sensor.tv_mode")
      ctime = self.time()
      stime = datetime.time(22,0,0)
      if workday=="off":
        etime = datetime.time(10,0,0)
      else:
        etime = datetime.time(7,0,0)
      #self.log("workday={}, tv={}, current time={}, start time={}, end time={}".format(workday,tv, ctime, stime,etime))
      #if self.anyone_home() and (ctime >= stime or ctime <= etime) and (tv is None or tv=="off"):
      if self.now_is_between ("20:00:00","07:00:00"):  
        self.log("setting sleep mode on")
        self.set_state("binary_sensor.sleep_mode", state="on")
        self.set_state("binary_sensor.announcement_mode", state="off")
      else:
        self.log("setting sleep mode off")
        self.set_state("binary_sensor.sleep_mode", state="off")
        self.set_state("binary_sensor.announcement_mode", state="on")
      
      if self.now_is_between ("00:00:00","07:00:00"):
        if self.get_state("switch.livingroom_aircon") == 'on':
          self.turn_off("switch.livingroom_aircon")

  
  def sleep_mode_change (self, entity, attribute, old, new, kwargs):
    self.log("sleep mode changed, updating sensor to {}".format(new))
    self.set_state("binary_sensor.sleep_mode", state=new)
    #self.cancel_timer(self.handler)
    self._auto = False


    

