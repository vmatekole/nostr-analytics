import json

from base.config import Settings
from nostr.event import Event

from .fixtures import (
    event_input_data_1,
    event_input_data_2,
    event_input_data_3,
    expected_bytes_for_input_data_1,
    expected_event_obj_3,
    expected_min_num_relays_10,
    expected_sig_for_input_data_1,
    kafka_event_topic,
    relay_seed_urls,
    reliable_relay_policy,
    reliable_relay_url,
)


class TestEvent:
    def test_to_json_bytes_str(
        self, event_input_data_1, expected_bytes_for_input_data_1
    ):
        result: bytes = Event(**event_input_data_1).to_json_bytes_str()
        assert result == expected_bytes_for_input_data_1

    def test_compute_id(self, event_input_data_1, expected_sig_for_input_data_1):  # type: ignore
        result: str = Event(**event_input_data_1).id
        assert result == expected_sig_for_input_data_1

    def test_parsing_event(self, event_input_data_3, expected_event_obj_3):
        json_array = json.loads(event_input_data_3)
        result: Event = Event.parse_event(json_array[2])
        assert result.model_dump() == expected_event_obj_3


class TestConfig:
    def test_read_config(self):
        config = Settings()

        assert (
            config.pub_key
            == 'bf8752cc0899f447a1254b5fcbc7d18c676a665166b5541fa57b461888a9fdfe'
        )
