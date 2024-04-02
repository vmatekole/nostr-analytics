import time
from typing import Any, Union

from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator, _EmptyRowIterator

from base.config import ConfigSettings, Settings
from nostr.event import Event
from nostr.relay import Relay
from services.bq import EventService, RelayService
from tests import biqquery

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
        assert event_service.insert_events([event])

    def test_event_tags_insert(self, event_bq_insert_data_2):
        assert Event.model_validate(event_bq_insert_data_2)
        event: Event = Event(**event_bq_insert_data_2)

        event_service = EventService(bigquery.Client())
        assert event_service.insert_events([event])

    def test_event_tags_complex_insert(self, event_bq_insert_data_3):
        assert Event.model_validate(event_bq_insert_data_3)
        event: Event = Event(**event_bq_insert_data_3)
        event_service = EventService(bigquery.Client())

        assert event_service.insert_events([event])

    # def test_bad_event_insert(self, event_bq_insert_data_1):
    #     config = Settings()
    #     assert Event.model_validate(event_bq_insert_data_1)
    #     event: Event = Event(**event_bq_insert_data_1)

    #     with pytest.raises(Exception):
    #         Event.persist_to_bigquery(
    #             [event], config.gcp_project_id,config.test_event_bq_dataset_id, config.test_event_bq_table_id
    #         )

    def test_event_bq_schema(self, event_bq_schema):
        assert Event.bq_schema() == event_bq_schema

    def test_bq_dump(self, event_bq_insert_data_2):
        event: Event = Event(**event_bq_insert_data_2)
        assert event.bq_dump() == {
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

    def test_bq_dump(self, discovered_relays):
        relay: Relay = discovered_relays[0]

        result = relay.bq_dump()
        assert result == {
            'country_code': 'USA',
            'latitude': '37.78035',
            'longitude': '-122.39059',
            'policy': {
                'read': True,
                'write': True,
            },
            'relay_name': None,
            'url': 'wss://relay.damus.io',
        }

    def test_insert_relay(self, discovered_relays):
        relay_service = RelayService(bigquery.Client())

        assert relay_service.insert_relays(discovered_relays)

    def test_get_relay(self):
        client = bigquery.Client()
        relay_service = RelayService(client)
        relays: list[Any] = relay_service.get_relays()
        relays[0].pop('inserted_at')  # inserted_at can change
        damus_relay = relays[0]
        assert damus_relay == {
            'relay_name': None,
            'relay_url': 'wss://relay.damus.io',
            'country_code': 'USA',
            'latitude': 37.78035,
            'longitude': -122.39059,
            'policy': {'read': True, 'write': True},
        }

    def test_update_relays_1(self, discovered_relays_without_geo_location):
        client = bigquery.Client()
        relay_service = RelayService(client)
        current_time = time.time()
        updated_name: str = f'updated_relay_name_at_{current_time}'
        relays: list[Relay] = discovered_relays_without_geo_location
        relays[0].relay_name = updated_name

        result_1: Union[
            RowIterator, _EmptyRowIterator, None
        ] = relay_service.update_relays(ConfigSettings.bq_dataset_id, relays)
        result_2: list[Any] = relay_service.get_relays()
        updated_relay = next(
            relay
            for relay in result_2
            if 'relay_name' in relay and relay['relay_name'] == updated_name
        )

        assert type(result_1) == _EmptyRowIterator
        assert updated_relay['relay_name'] == updated_name
