import json
import uuid
from typing import Literal

import pytest

from base.config import ConfigSettings
from nostr.event import EventKind
from nostr.filter import Filter, Filters
from nostr.message_pool import EventMessage
from nostr.relay import Relay
from nostr.relay_manager import RelayManager

from .fixtures import (
    damus_relay,
    damus_relay_url,
    event_input_data_1,
    event_input_data_2,
    event_input_data_3,
    expected_bytes_for_input_data_1,
    expected_event_obj_3,
    expected_sig_for_input_data_1,
    kafka_event_topic,
    relay_seed_urls,
    reliable_relay_policy,
    reliable_relay_url,
)


class TestNostrNetwork:
    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_relay_connect(self, reliable_relay_url):
        relay_manager: RelayManager = RelayManager()
        relay_manager.add_relay(reliable_relay_url)

        result: Relay = relay_manager.relays[reliable_relay_url]['relay']

        assert result.ws.sock.connected == True

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_follow_up_req(
        self,
        reliable_relay_url: Literal['wss://relay.damus.io'],
        reliable_relay_policy: dict[str, bool],
    ):
        relay_manager: RelayManager = RelayManager()
        filters = Filters(initlist=[Filter(kinds=[EventKind.CONTACTS])])
        relay_manager.add_relay(reliable_relay_url)

        relay_manager.add_subscription_on_all_relays(
            id=str(uuid.uuid4()), filters=filters
        )
        event_msg: EventMessage = None
        result: list = None
        while True:
            if relay_manager.message_pool.has_events():
                event_msg: EventMessage = relay_manager.message_pool.get_event()
                if not event_msg.event.content == '':
                    result: dict = json.loads(event_msg.event.content)
                    break
        assert len(result) > 7
        assert result.get(reliable_relay_url) == reliable_relay_policy

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_get_geo_location_info_for_a_relay(self, damus_relay: str):
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

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_geo_location_discovered(self, reliable_relay_url):
        relay_manager: RelayManager = RelayManager()
        relay_manager.add_relay(reliable_relay_url)

        result: Relay = relay_manager.relays[reliable_relay_url]['relay']

        assert result.country_code == 'USA'

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_relay_manager_does_not_duplicate_to_db(self, mocker, damus_relay_url):
        relay_manager: RelayManager = RelayManager()

        mocked_relay_service = mocker.patch('services.bq.RelayService.save_relays')
        relay_manager.add_relay(damus_relay_url)

        mocked_relay_service.save_relays.assert_not_called()  # type: ignore
        relay_manager.close_all_relay_connections()
