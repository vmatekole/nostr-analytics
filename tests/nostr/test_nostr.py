import json
import re
import unittest
from dataclasses import asdict
from unittest import result

from models.nostr.event import Event
from models.nostr.relay import Relay
from models.nostr.relay_manager import RelayManager
from utils import Logger

from .fixtures import (
    event_input_data_1,
    event_input_data_3,
    expected_bytes_for_input_data_1,
    expected_event_obj_3,
    expected_sig_for_input_data_1,
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

    def test_relay_connect(self):
        relay_manager = RelayManager()
        relay_manager.add_relay('wss://relay.damus.io')

        result = relay_manager.relays['wss://relay.damus.io']

        assert result.ws.sock.connected == True
