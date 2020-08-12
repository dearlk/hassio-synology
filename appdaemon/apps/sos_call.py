import appdaemon.plugins.hass.hassapi as hass
import myglobals
from datetime import datetime, time, timedelta


# SOSCall App
#
# Args:
#

class SOSCall(hass.Hass):

  def initialize(self):
    self.log("Initializing...")

    self.message = "" 
    self.repeater = self.get_state("input_number.sos_call_repeater")
    self.interval = self.get_state("input_number.sos_call_interval")
    self.counter = 0
    self.__handler = None 

    self.log("message={},repeater={},interval={}".format(self.message, self.repeater, self.interval))
    self.listen_state(self.callb, "input_boolean.sos_call", old="off", new="on")
    
  def callb (self, entity, attribute, old, new, kwargs):
    self.message = self.get_state("input_text.sos_message")

    if self.message is None or "":
      self.message="SOS call here, Jyoti is calling. Please attend her immediately!!!"
    
    self.current_state = self.get_tracker_state("device_tracker.jyoti")
    self.log("current_state={}".format(self.current_state))

    #at home
    if self.current_state != "not_home":
      self.room_name = self.get_state("sensor.jyoti_room_location")
      self.log("room_name={}".format(self.room_name))
      self.message = self.message + " She is currently at home and inside {}".format(self.room_name)
    #not at home
    else:
      self.location = self.get_state("sensor.jyoti")
      self.log("location={}".format(self.location))
      self.message = self.message + " She is currently at {}".format(self.location)

    self.log("message={}".format(self.message))
    Run_When=datetime.now()+timedelta(seconds=5)
    self.__handler = self.run_every(self.send_sos, Run_When, float(self.interval) * 60)


  def send_sos (self, kwargs):
    self.log("invoked...")
    shield_tv_muted=0
    fire_tv_muted=0
    home_group_available=0
    shield_tv_state   = self.get_state("media_player.shield_tv")
    fire_tv_state     = self.get_state("media_player.fire_tv")
    home_group_state  = self.get_state("media_player.home")
    self.log("shield_tv_state={},fire_tv_state={},home_group_state={}".format(shield_tv_state,fire_tv_state,home_group_state))
    
    #check if shield tv running then mute it
    if shield_tv_state is not None and shield_tv_state != "unavailable":
      self.log("muting shield tv...")
      self.call_service("media_player/volume_mute", entity_id="media_player.shield_tv", is_volume_muted=True)
      shield_tv_muted=1
      self.log("done")
    
    #check if fire tv running then mute it
    if fire_tv_state is not None and fire_tv_state != "unavailable":
      self.log("muting fire tv...")
      self.call_service("media_player/volume_mute", entity_id="media_player.fire_tv", is_volume_muted=True)
      fire_tv_muted=1
      self.log("done")
    
    #check if google home group 'home' is avaiable then send message
    if home_group_state is not None and home_group_state != "unavailable":
      self.log("Home group is available...broadcasting messages...")
      home_group_available=1
      #set volume to 100%
      self.call_service("media_player/volume_set", entity_id="media_player.home", volume_level=1.0)
      #start with alarm music bell
      media_content_id_path = self.get_state("variable.base_url_full") + "/local/alert-4.mp3"
      self.log(media_content_id_path)
      handle = self.run_sequence([{"media_extractor/play_media": {"entity_id": "media_player.home", "media_content_id": media_content_id_path, "media_content_type": "music"}}, 
                                  {"sleep": 4}, 
                                  {"python_script/notify":{"message": self.message, "announce": "1", "override": "1"}},
                                  {"sleep": 12},
                                  {"media_extractor/play_media": {"entity_id": "media_player.home", "media_content_id": media_content_id_path, "media_content_type": "music"}},
                                  {"sleep": 4}
                                ])
    self.log("sending MQTT alarm...")
    handle = self.run_sequence([ 
                                  {"mqtt/publish":{"topic": "zanzito/lalit/alarm/play", "payload": self.message, "namespace":"mqtt"}},
                                  {"sleep": 30}, 
                                  {"mqtt/publish":{"topic": "zanzito/lalit/alarm/stop", "payload": self.message, "namespace":"mqtt"}}
                                ])
    #self.call_service("mqtt/publish", topic="zanzito/lalit/alarm/play", payload=self.message, namespace="mqtt")

    if shield_tv_muted==1:
      self.log("unmuting shield tv...")
      self.call_service("media_player/volume_mute", entity_id="media_player.shield_tv", is_volume_muted=False)
    if fire_tv_muted==1:
      self.log("unmuting fire tv...")
      self.call_service("media_player/volume_mute", entity_id="media_player.fire_tv", is_volume_muted=False)

    self.counter = self.counter + 1
    self.log("counter={}, repeater={}".format(self.counter,float(self.repeater)))
    #turn off trigger and reset counter now
    if self.counter >= float(self.repeater):
      self.turn_off(entity_id="input_boolean.sos_call")  
      self.cancel_timer(self.__handler)
      self.counter = 0

    






    
    