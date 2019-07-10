import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta
import globals

class utils(hass.Hass):

  def initialize(self):
    pass

  def logger (message, kwargs):
    if "notify" in kwargs and int(kwargs["notify"]) == 1:
      self.log(message)
      self.notify(message, name=globals.notify)
    else:
      self.log(message)	      
    