import json
import unittest
from dataclasses import asdict
from unittest import result

import pytest

from models.nostr.event import Event

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
