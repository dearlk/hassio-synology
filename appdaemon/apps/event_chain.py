"""Define automations for chain event triggers."""

from datetime import datetime
from typing import Union

import voluptuous as vol
from appdaemon.plugins.hass.hassapi import Hass


CONF_CLASS = 'class'
CONF_MODULE = 'module'

CONF_ACTION = 'action'
CONF_DELAY = 'delay'
#CONF_PARAMETERS = 'parameters'
CONF_SERVICE = 'service'
CONF_TIMEFRAME = 'timeframe'

CONF_ENTITY_ID = 'entity_id'
CONF_EVENT = 'event'
CONF_EVENTS = 'events'
CONF_RANK = 'rank'
CONF_TARGET_STATE = 'target_state'

APP_SCHEMA = vol.Schema({
    vol.Required(CONF_MODULE): str,
    vol.Required(CONF_CLASS): str,
    vol.Required(CONF_TIMEFRAME): int,
    vol.Required(CONF_ACTION): vol.Schema({
        vol.Required(CONF_ENTITY_ID): str,
        vol.Required(CONF_SERVICE): str,
        vol.Optional(CONF_DELAY): int,
        #vol.Optional(CONF_PARAMETERS): dict,
    }),
    vol.Required(CONF_EVENTS): vol.Schema({
        vol.Optional(str): vol.Schema({
            vol.Required(CONF_ENTITY_ID): str,
            vol.Optional(CONF_TARGET_STATE): str,
            vol.Optional(CONF_RANK): int,
        }, extra=vol.ALLOW_EXTRA),
    }),
}, extra=vol.ALLOW_EXTRA)


class EventChain(Hass):
    """ Define a base feature for event-chain based automations."""

    APP_SCHEMA = APP_SCHEMA

    def initialize(self) -> None:
        """Initialize."""

        # Check if the app configuration is correct:
        try:
            self.APP_SCHEMA(self.args)
        except vol.Invalid as err:
            self.error(f"Invalid Format: {err}", level='ERROR')
            return

        # Define holding place for the event trigger timestamps
        self.event_timestamps = {}

        # Get the action configuration
        action_conf = self.args[CONF_ACTION]
        self.action = action_conf[CONF_SERVICE]
        self.action_entity = action_conf[CONF_ENTITY_ID]
        #self.action_param = action_conf[CONF_PARAMETERS]
        self.delay = action_conf.get(CONF_DELAY)

        # Get the timeframe
        self.timeframe = self.args[CONF_TIMEFRAME]

        # Get the highest rank from the event dictionary:
        events = self.args.get('events', {})
        self.max_rank = max([
            attribute[CONF_RANK] for event, attribute in events.items()
        ])

        for event, attribute in events.items():
            self.listen_state(
                self.event_triggered,
                attribute[CONF_ENTITY_ID],
                new=attribute[CONF_TARGET_STATE],
                rank=attribute[CONF_RANK]
            )

    def event_triggered(self, entity: Union[str, dict], attribute: str, old: str, new: str, kwargs: dict) -> None:
        """Determine next action based on rank of the triggered event."""
        
        rank = kwargs[CONF_RANK]
        self.update_event_trigger_timestamp(rank)
        if rank == self.max_rank:
            self.log('max rank')
            if self.all_events_triggered_in_timeframe:
                self.event_timestamps.clear()
                if self.delay:
                    self.run_in(self.fire_action, self.delay)
                else:
                    self.fire_action()

    def fire_action(self,kwargs) -> None:
        """Fires the specified action."""
        self.call_service(
            f"{self.action_entity.split('.')[0]}/{self.action}",
            entity_id=self.action_entity
        )
        self.log(f"{self.action} {self.action_entity} executed.")

    def update_event_trigger_timestamp(self, rank: int) -> None:
        """Updates timestamp of triggered event in the event timelist."""
        event_name = f"event_{str(rank)}"
        self.event_timestamps[event_name] = datetime.now()

    def all_events_triggered_in_timeframe(self) -> bool:
        """Returns true if all events triggered within timeframe and in order."""
        return (
            self.all_events_triggered and
            self.in_timeframe and
            self.triggered_in_order
        )
            
    def all_events_triggered(self) -> bool:
        """Returns true if all events have been triggered."""
        return len(self.event_timestamps) == self.max_rank

    def in_timeframe(self) -> bool:
        """Returns True if events within timeframe."""
        tstp_first_event = self.event_timestamps['event_1']
        tstp_last_event = self.event_timestamps[f"event_{str(self.max_rank)}"]

        return (tstp_last_event - tstp_first_event).total_seconds() < self.timeframe

    def triggered_in_order(self) -> bool:
        """Returns True if all events where triggered in order."""
        sorted_timestamps = [
            self.event_timestamps[event] for event
            in sorted(self.event_timestamps.keys())
        ]

        return all(
            sorted_timestamps[i] <= sorted_timestamps[i + 1] for i
            in range(len(sorted_timestamps)-1)
        )