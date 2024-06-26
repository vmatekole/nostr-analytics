import re
import time
from typing import Any, Union

import pytest
from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator, _EmptyRowIterator

from base.config import ConfigSettings, Settings
from base.utils import logger
from nostr.event import Event
from nostr.relay import Relay, RelayPolicy
from services.bq import EventService, RelayService

from .fixtures import (
    discovered_relays,
    discovered_relays_without_geo_location,
    event_bq_insert_data_1,
    event_bq_insert_data_2,
    event_bq_insert_data_3,
    event_bq_schema,
)


class TestBiqQuery:
    def test_insert_event(self, event_bq_insert_data_1):
        assert Event.model_validate(event_bq_insert_data_1)
        event: Event = Event(**event_bq_insert_data_1)

        event_service = EventService(bigquery.Client())
        assert event_service.save_events([event])

    def test_event_tags_insert(self, event_bq_insert_data_2):
        assert Event.model_validate(event_bq_insert_data_2)
        event: Event = Event(**event_bq_insert_data_2)

        event_service = EventService(bigquery.Client())
        assert event_service.save_events([event])

    def test_event_tags_complex_insert(self, event_bq_insert_data_3):
        assert Event.model_validate(event_bq_insert_data_3)
        event: Event = Event(**event_bq_insert_data_3)
        event_service = EventService(bigquery.Client())

        assert event_service.save_events([event])

    def test_to_dict(self, event_bq_insert_data_2):
        event: Event = Event(**event_bq_insert_data_2)
        assert event.to_dict() == {
            'content': 'Sample content with tags',
            'created_at': 1709145700,
            'kind': 1,
            'pubkey': 'bf8752cc0899f447a1254b5fcbc7d18c676a665166b5541fa57b461888a9fdfe',
            'sig': None,
            'tags': [
                {
                    'tag_id': 0,
                    'tag_values': [
                        'tag6',
                        'tag7',
                    ],
                },
                {
                    'tag_id': 1,
                    'tag_values': [
                        'tag8',
                        'tag9',
                        'tag10',
                    ],
                },
            ],
        }

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_to_dict(self, discovered_relays):
        ConfigSettings.relay_refresh_ip_geo_relay_info = True
        relay: Relay = discovered_relays[0]

        result = relay.to_dict()

        assert result['country_code'] == 'USA'
        assert result['latitude'] == '37.78035'
        assert result['longitude'] == '-122.39059'
        assert result['url'] == 'wss://relay.damus.io'
        assert result['policy']['read'] == True
        assert result['policy']['write'] == True
        assert result['country_code'] == 'USA'

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_insert_relay(self, discovered_relays):
        relay_service = RelayService(bigquery.Client())

        assert relay_service.save_relays(discovered_relays)

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_get_relay(self):

        relay_name = f'test-ran{time.time()}'
        relay = Relay(
            name=relay_name,
            url='wss://test_relay_is_added.wine',
        )

        relay_service = RelayService(bigquery.Client())

        relay_service.save_relays([relay])

        relays: list[Relay] = relay_service.get_relays()

        assert relays

        relay: Relay = next(relay for relay in relays if relay.name == relay_name)

        wine_relay = {'name': relay.name, 'policy': relay.policy}

        assert wine_relay == {
            'name': relay_name,
            'policy': RelayPolicy(should_read=True, should_write=False),
        }

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_update_relays_1(self, discovered_relays_without_geo_location):
        client = bigquery.Client()
        relay_service = RelayService(client)
        current_time = time.time()
        updated_name: str = f'updated_name_at_{current_time}'
        relays: list[Relay] = discovered_relays_without_geo_location
        relays[0].name = updated_name

        result_1: Union[
            RowIterator, _EmptyRowIterator, None
        ] = relay_service.update_relays(ConfigSettings.bq_dataset_id, relays)
        result_2: list[Any] = relay_service.get_relays()

        updated_relay = None
        for relay in result_2:
            if relay.name and relay.name == updated_name:
                updated_relay = relay

        # assert type(result_1) == _EmptyRowIterator
        assert updated_relay.name == updated_name
