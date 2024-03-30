import json
from typing import Literal

from analytics import Analytics
from models.nostr.event import EventKind
from models.nostr.filter import Filters
from models.nostr.message_pool import EventMessage
from models.nostr.relay import Relay
from models.nostr.relay_manager import RelayManager

from .fixtures import (
    damus_relay,
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


class TestNostrNetwork:
    def test_relay_connect(self, reliable_relay_url):
        relay_manager: RelayManager = RelayManager()
        relay_manager.add_relay(reliable_relay_url)

        result: Relay = relay_manager.relays[reliable_relay_url]

        assert result.ws.sock.connected == True

    def test_follow_up_req(
        self,
        reliable_relay_url: Literal['wss://relay.damus.io'],
        reliable_relay_policy: dict[str, bool],
    ):
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
        assert len(result) > 7
        assert result.get(reliable_relay_url) == reliable_relay_policy

    def test_get_relays(self, relay_seed_urls, expected_min_num_relays_10):
        analytics: Analytics = Analytics()

        relays = analytics.discover_relays(relay_seed_urls)

        assert len(relays) >= 1000

    def test_get_geo_location_info_for_a_relay(self, damus_relay):
        expected_result = {
            'calling_code': '+1',
            'city': 'San Francisco',
            'continent_code': 'NA',
            'continent_name': 'North America',
            'country_capital': 'Washington, D.C.',
            'country_code2': 'US',
            'country_code3': 'USA',
            'country_name': 'United States',
            'country_name_official': 'United States of America',
            'country_tld': '.us',
        }

        damus_info = Relay.get_relay_geo_info([damus_relay])

        assert damus_info[0]['calling_code'] == expected_result['calling_code']
        assert damus_info[0]['continent_name'] == expected_result['continent_name']
        assert damus_info[0]['country_code2'] == expected_result['country_code2']
        assert damus_info[0]['country_name'] == expected_result['country_name']

    def test_geo_location_discovered(self, reliable_relay_url):
        relay_manager: RelayManager = RelayManager()
        relay_manager.add_relay(reliable_relay_url)

        result: Relay = relay_manager.relays[reliable_relay_url]

        # assert result.ws.sock.connected == True

        assert result.country == 'US'
