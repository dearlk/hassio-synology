import appdaemon.plugins.hass.hassapi as hass
import datetime
from datetime import datetime as dt
import myglobals

class Notify(hass.Hass):

  def initialize(self):
    self.set_state("sensor.appd_notify",state="Appdaemon started !",attributes={"announce":True})
    self.listen_state(self.send_notify,"sensor.appd_notify")

  def send_notify(self, entity, attribute, old, new, kwargs):
    self.notify(new, name=myglobals.notify_service)
    tts_trigger = self.get_state(entity,attribute="announce")
    ha_trigger = self.get_state(entity,attribute="frontend")
    announcement_mode = self.get_state("binary_sensor.announcement_mode")
    broadcast_mode = self.get_state("input_select.broadcast_mode")
    sleep_mode = self.get_state("binary_sensor.sleep_mode")
    if sleep_mode is None:
      sleep_mode = self.get_state("input_boolean.sleep_mode")

    self.log("broadcast_mode={},Frontend={},Announce={},announcement_mode={},sleep_mode={},message={}".format(broadcast_mode,ha_trigger,tts_trigger,announcement_mode,sleep_mode,new))
    
    if tts_trigger and announcement_mode == "on" and  sleep_mode=="off":
      self.call_service('script/turn_on', entity_id='script.tv_mute')
      self.call_service('media_player/volume_set', entity_id='media_player.livingroom', volume_level=1.0)
      if broadcast_mode == "Assistant":
        self.notify(new,name="google_broadcast")
      elif broadcast_mode == "TTS":
        self.call_service("tts/google_say", entity_id='media_player.livingroom', message=new)
      self.run_in(self.call_service('script/turn_on', entity_id='script.tv_mute'), 5)
      #self.call_service('script/turn_on', entity_id='script.tv_mute')

    if ha_trigger:
      self.call_service('persistent_notification/create', title="Attention", message=new+ " - " + dt.now().strftime('%I:%M %p') )
    