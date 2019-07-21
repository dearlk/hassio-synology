VERSION = '1.0.0'

ATTR_TEXT     = 'text'
ATTR_TELL     = 'tell'
ATTR_SHOW     = 'show'
ATTR_ANNOUNCE = 'announce'
ATTR_ROOM     = 'room'
ATTR_MESSAGE  = 'message'
ATTR_PRESENCE_CHECK = 'presence_check'

text = data.get(ATTR_TEXT) 
tell = data.get(ATTR_TELL) 
show = data.get(ATTR_SHOW) 
announce = data.get(ATTR_ANNOUNCE) 
room = data.get(ATTR_ROOM) 
message = data.get(ATTR_MESSAGE) 
presence_check = data.get(ATTR_PRESENCE_CHECK)
service_data = {'message': message}


IS_ANYONE_HOME = False
# check configuration setup in HA
BROADCAST_AGENT = hass.states.get("input_select.broadcast_agent").state
BROADCAST_MODE = hass.states.get("input_select.broadcast_mode").state
BROADCAST_SPEAKER = hass.states.get("input_select.broadcast_speaker").state
sleep_mode = hass.states.get("binary_sensor.sleep_mode").state
announcement_mode = hass.states.get("binary_sensor.announcement_mode").state
home_group_state = hass.states.get("media_player.home").state
#logger.info ("home_group_state={}".format(home_group_state))

#define the rule
jyoti_at_home = hass.states.get("device_tracker.jyoti").state
lalit_at_home = hass.states.get("device_tracker.lalit").state
if jyoti_at_home == "home" or lalit_at_home == "home":
  IS_ANYONE_HOME = True

BROADCAST_SPEAKER = "media_player." + BROADCAST_SPEAKER
logger.info("Initializing now..................................................................................")
logger.info("BROADCAST_AGENT={}, BROADCAST_MODE={}, BROADCAST_SPEAKER={}".format(BROADCAST_AGENT,BROADCAST_MODE,BROADCAST_SPEAKER))
logger.info("text={}, tell={}, show={}, announce={}, room={}, message={}, presence_check={}".format(text,tell,show,announce,room, message,presence_check))
logger.info("sleep_mode={}, announcement_mode={}, speaker={}".format(sleep_mode,announcement_mode,BROADCAST_SPEAKER))
logger.info("IS_ANYONE_HOME={}".format(IS_ANYONE_HOME))


#text####################################################################################
if (text is not None and int(text)==1) or (BROADCAST_MODE == "TEXT" or BROADCAST_MODE == "ALL"):
  if tell is not None:
    to = tell
  else:
    to = "ha_notifier"
  logger.info("sending text now...")  
  service_data = {'message': message}  
  hass.services.call('notify', to, service_data, False)	
  

#announce#################################################################################### 
if announce is not None and int(announce)==1 or (BROADCAST_MODE == "ANNOUNCE" or BROADCAST_MODE == "ALL"):
  if announcement_mode=='on' and IS_ANYONE_HOME:
    logger.info("announcing now...")  
    if BROADCAST_AGENT == "google_broadcast":
      service_data = {'message': message}
      hass.services.call('notify', BROADCAST_AGENT, service_data)
    else:
      # if "<speak>" not in message:
      #   message = "<speak>" + message + "</speak>"
      service_data = {'message': message, 'entity_id': BROADCAST_SPEAKER}
      while True:
        if hass.states.get(BROADCAST_SPEAKER).state == "playing":
          time.sleep(1)
          logger.info("looks like media player busy... waiting")
          continue
        else:
          logger.info("ok, media player available now...")
          break  
      hass.services.call('tts', BROADCAST_AGENT, service_data, False)  


###############################################################################################
#no flag passed, do all
#if (text is None and show is None and announce is None) or (BROADCAST_MODE == "ALL"):
# if BROADCAST_MODE=="ALL":
#   if message is not None:
#     logger.info("sending text now...")
#     to = "ha_notifier"
#     service_data = {'message': message}  
#     hass.services.call('notify', to, service_data, False)	    
#     if announcement_mode=='on' and IS_ANYONE_HOME:
#       logger.info("announcing now...")
#       if "<speak>" not in message:
#         message = "<speak>" + message + "</speak>"
#       if BROADCAST_AGENT == "google_broadcast":
#         service_data = {'message': message}
#         hass.services.call('notify', BROADCAST_AGENT, service_data)
#       else:
#         service_data = {'message': message, 'entity_id': BROADCAST_SPEAKER}
#         while True:
#           if hass.states.get(BROADCAST_SPEAKER).state == "playing":
#             time.sleep(1)
#             logger.info("looks like media player busy... waiting")
#             continue
#           else:
#             logger.info("ok, media player available now...")
#             break  
#         hass.services.call('tts', BROADCAST_AGENT, service_data, False)   
logger.info("Ending now.........................................................................................")