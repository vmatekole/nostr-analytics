import json
import re
import time
import unittest
from dataclasses import asdict
from unittest import result
from urllib import request

from models.nostr.event import Event, EventKind
from models.nostr.filter import Filter, Filters
from models.nostr.message_pool import EventMessage
from models.nostr.relay import Relay
from models.nostr.relay_manager import RelayManager
from models.nostr.request import Request
from utils import Logger

from .fixtures import (
    event_input_data_1,
    event_input_data_3,
    expected_bytes_for_input_data_1,
    expected_event_obj_3,
    expected_sig_for_input_data_1,
    reliable_relay_policy,
    reliable_relay_url,
)


class TestEvent:
    def test_to_bytes(self, event_input_data_1, expected_bytes_for_input_data_1):

        result: bytes = Event(**event_input_data_1).to_bytes()
        assert result == expected_bytes_for_input_data_1

    def test_compute_id(self, event_input_data_1, expected_sig_for_input_data_1):  # type: ignore
        result: str = Event(**event_input_data_1).id
        assert result == expected_sig_for_input_data_1

    def test_parsing_event(self, event_input_data_3, expected_event_obj_3):
        json_array = json.loads(event_input_data_3)

        result: Event = Event.parse_event(json_array[2])

        assert asdict(result) == expected_event_obj_3

    def test_relay_connect(self, reliable_relay_url):
        relay_manager: RelayManager = RelayManager()
        relay_manager.add_relay(reliable_relay_url)

        result: Relay = relay_manager.relays[reliable_relay_url]

        assert result.ws.sock.connected == True

    def test_follow_up_req(self, reliable_relay_url, reliable_relay_policy):
        relay_manager: RelayManager = RelayManager()
        filters = Filters(initlist=[Filter(kinds=[EventKind.CONTACTS])])
        relay_manager.add_relay(reliable_relay_url)

        relay_manager.add_subscription_on_all_relays(id='foo', filters=filters)
        event_msg: EventMessage = None
        result: list = None
        while True:
            if relay_manager.message_pool.has_events():
                event_msg: EventMessage = relay_manager.message_pool.get_event()
                result: dict = json.loads(event_msg.event.content)
                break
        assert len(result) > 0
        assert result.get(reliable_relay_url) == reliable_relay_policy
