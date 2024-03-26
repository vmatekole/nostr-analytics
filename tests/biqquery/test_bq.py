from config import Settings
from models.nostr.event import Event
from utils import logger

from .fixtures import event_bq_schema


class TestBiqQuery:
    def test_event_insert(self, event_bq_insert_data_1):
        config = Settings()
        assert Event.model_validate(event_bq_insert_data_1)
        event: Event = Event(**event_bq_insert_data_1)

        assert Event.persist_to_bigquery(
            [event], config.TEST_EVENT_BQ_DATATSET_ID, config.TEST_EVENT_BQ_TABLE_ID
        )

    def test_event_bq_schema(self, event_bq_schema):
        assert Event.bq_schema() == event_bq_schema
