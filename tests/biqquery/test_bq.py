from google.cloud import bigquery

from client.bq import Bq
from config import ConfigSettings, Settings
from models.bigquery.utils import BqUtils
from models.nostr.event import Event
from models.nostr.relay import Relay
from services.bq import RelayService
from utils import logger

from .fixtures import (
    event_bq_insert_data_1,
    event_bq_insert_data_2,
    event_bq_insert_data_3,
    event_bq_schema,
)


class TestBiqQuery:
    def test_event_insert(self, event_bq_insert_data_1):
        config = Settings()
        assert Event.model_validate(event_bq_insert_data_1)
        event: Event = Event(**event_bq_insert_data_1)

        assert BqUtils.persist_to_bigquery(
            [event],
            config.gcp_project_id,
            config.bq_dataset_id,
            config.bq_event_table_id,
        )

    def test_event_tags_insert(self, event_bq_insert_data_2):
        config = ConfigSettings
        assert Event.model_validate(event_bq_insert_data_2)
        event: Event = Event(**event_bq_insert_data_2)

        assert BqUtils.persist_to_bigquery(
            [event],
            config.gcp_project_id,
            config.bq_dataset_id,
            config.bq_event_table_id,
        )

    def test_event_tags_complex_insert(self, event_bq_insert_data_3):
        config = ConfigSettings
        assert Event.model_validate(event_bq_insert_data_3)
        event: Event = Event(**event_bq_insert_data_3)

        assert BqUtils.persist_to_bigquery(
            [event],
            config.gcp_project_id,
            config.bq_dataset_id,
            config.bq_event_table_id,
        )

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

    def test_bq_get_relays(self):
        client = bigquery.Client()
        bq_service = RelayService(client)
        relays = bq_service.get_relays()

        assert relays == []
