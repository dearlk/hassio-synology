import appdaemon.plugins.hass.hassapi as hass
import myglobals
from datetime import datetime, time, timedelta

# ServiceListener App
#
# Args:
#

class CameraScanner(hass.Hass):

  def initialize(self):
    self.log("Initializing...")
    self.counter=2
    Run_When=datetime.now()+timedelta(seconds=5)
    self.run_every(self.callb,Run_When, 1*60)

    

  def callb(self, kwargs):
    self.log(self.counter)
    try:
      if self.counter % 2 == 0:
        self.log("scanning livingroom camera...")
        self.call_service("image_processing/scan", entity_id="image_processing.deepstackfd_livingroom")
        self.call_service("image_processing/scan", entity_id="image_processing.deepstackod_livingroom")
        self.call_service("image_processing/scan", entity_id="image_processing.facebox_livingroom")
      else:
        self.log("scanning bedroom camera...")
        self.call_service("image_processing/scan", entity_id="image_processing.deepstackfd_bedroom")
        self.call_service("image_processing/scan", entity_id="image_processing.deepstackod_bedroom")
        self.call_service("image_processing/scan", entity_id="image_processing.facebox_bedroom")
    except:
      self.log("error occured")  
    finally:  
      self.counter = self.counter+1





