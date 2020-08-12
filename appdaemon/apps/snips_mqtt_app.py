import appdaemon.plugins.hass.hassapi as hass
import appdaemon.plugins.mqtt.mqttapi as mqtt
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
import json
import os.path
from pathlib import Path
from os import path
import operator
import io
import sys,getopt
import random

#import hermes-python
# SnipsMQTTApp App
#
# Args:
#

class SnipsMQTTApp(hass.Hass):

  def initialize(self):
    self.log("monitoring MQTT messages for Snips...")
    self._modelId = None
    self._siteId = None
    self._yes_response_messages = [ "Consider done", "ok, done",  "It was easy", "it's done", "oh, it was easy!" ]
    self._no_response_messages = [ "Ok, nevemind", "As you say",  "you're the boss", "not a problem", "got it"  ]
    self._start_greeting = [ "I am starting now",  "I am up now",  "hey it's Jarvis here!!!" ]

    self.listen_event(self.intent_received, "MQTT_MESSAGE", topic = 'hermes/nlu/intentParsed', namespace="mqtt")
    self.listen_event(self.yesResponse_intent_received, "MQTT_MESSAGE", topic = 'hermes/intent/dearlk:yesResponse', namespace="mqtt")
    self.listen_event(self.noResponse_intent_received, "MQTT_MESSAGE", topic = 'hermes/intent/dearlk:noResponse', namespace="mqtt")
    self.listen_event(self.waitResponse_intent_received, "MQTT_MESSAGE", topic = 'hermes/intent/dearlk:waitResponse', namespace="mqtt")
    
    self.listen_event(self.hotword_detected, "MQTT_MESSAGE", topic = 'hermes/hotword/default/detected', namespace="mqtt")
    

    self.call_service("mqtt/publish", topic="hermes/dialogueManager/startSession", payload=json.dumps({'init':{'type':'notification','text':random.choice(self._start_greeting)}}))
    
#############################################################  
  def hotword_detected(self, event_name, data, kwargs):
    self.log("----------------------------------------------------------------------------------------") 
    payload = json.loads(data['payload'])
    self._modelId = payload.get("modelId")
    self._siteId = payload.get("siteId")
    #response = json.dumps( {'init':{'type':'action','text':'yes babu ji main {} hoon, kahiye'.format(modelId), 'canBeEnqueued':True, 'sendIntentNotRecognized':True}} )
    #self.call_service("mqtt/publish", topic="hermes/dialogueManager/startSession", payload=response)
    self.log("----------------------------------------------------------------------------------------")       

#############################################################  
  def intent_received(self, event_name, data, kwargs):
    self.log("----------------------------------------------------------------------------------------") 
    payload = json.loads(data['payload'])
    intent = payload.get("intent")["intentName"]
    sessionId = payload.get('sessionId')
    #self.log("payload={},sessionId={},intent={}".format(payload, sessionId, intent))
    self.log(data)
    if intent == "dearlk:welcome":
      response = json.dumps({'sessionId':sessionId,'text':'hello, main {}! Aap aaj kaise hain?'.format(self._modelId),'sendIntentNotRecognized':True})
      self.call_service("mqtt/publish", topic="hermes/dialogueManager/continueSession", payload=response)
    elif intent == "dearlk:welcomeResponse":
      response = json.dumps({'sessionId':sessionId,'text':'jaan kar khushi hui!'})
      self.call_service("mqtt/publish", topic="hermes/dialogueManager/endSession", payload=response)
    self.log("----------------------------------------------------------------------------------------")       

#############################################################  
  def yesResponse_intent_received(self, event_name, data, kwargs):
    self.log("----------------------------------------------------------------------------------------") 
    self.log(data)
    payload = json.loads(data['payload'])
    #intent = payload.get("intent")["intentName"]
    sessionId = payload.get('sessionId')
    customData = payload.get("customData")
    action, room, entity = customData.split(" ")
    self._actions = {"turn_on": "turning on", "switch_on": "switching on", "turn_off": "turning off","switch_off": "switching off"}
    reply = "Ok, {} {} {}".format(self._actions[action],room, entity)    
    self.log(reply)
    #self.log("payload={},sessionId={},intent={}".format(payload, sessionId, intent))
    self.log(data)
    response = json.dumps({'sessionId':sessionId,'text':reply})
    self.call_service("mqtt/publish", topic="hermes/dialogueManager/endSession", payload=response)
    # action here
    response = json.dumps({'init':{'type':'notification','text':random.choice(self._yes_response_messages)}})
    self.call_service("mqtt/publish", topic="hermes/dialogueManager/startSession", payload=response)
    self.log("----------------------------------------------------------------------------------------")       

#############################################################  
  def noResponse_intent_received(self, event_name, data, kwargs):
    self.log("----------------------------------------------------------------------------------------") 
    payload = json.loads(data['payload'])
    #intent = payload.get("intent")["intentName"]
    sessionId = payload.get('sessionId')
    #self.log("payload={},sessionId={},intent={}".format(payload, sessionId, intent))
    self.log(data)
    response = json.dumps({'sessionId':sessionId,'text':random.choice(self._no_response_messages)})
    self.call_service("mqtt/publish", topic="hermes/dialogueManager/endSession", payload=response)
    self.log("----------------------------------------------------------------------------------------")       

#############################################################  
  def waitResponse_intent_received(self, event_name, data, kwargs):
    self.log("----------------------------------------------------------------------------------------") 
    payload = json.loads(data['payload'])
    sessionId = payload.get('sessionId')
    value = payload.get("slots")[0]["value"]
    for k in value:
      if k != "kind" and k != "precision":
        if int(value[k]) > 0:
          period, duration=k,int(value[k])
          break
    self.log("value={},period={},duration={}".format(value, period, duration))
    #self.log(data)
    response = json.dumps({'sessionId':sessionId,'text':'ok will do after {} {}'.format(duration, period)})
    self.call_service("mqtt/publish", topic="hermes/dialogueManager/endSession", payload=response)
    self.log("----------------------------------------------------------------------------------------")       
