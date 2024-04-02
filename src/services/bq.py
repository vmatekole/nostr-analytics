import json
from time import sleep
from typing import Any, Union

from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator, _EmptyRowIterator

from client.bq import Bq
from config import ConfigSettings, Settings
from models.nostr.relay import Relay
from models.sql import RelaySQL
from utils import logger


class BqService:
    def __init__(self, client) -> None:
        self._client = client
        self._bq = Bq(client)


class RelayService(BqService):
    def __init__(self, client) -> None:
        super().__init__(client)

    def get_relays(self) -> list[Any]:
        result = list(
            self._bq.run_sql(
                RelaySQL.select_all_from(
                    ConfigSettings.bq_dataset_id, ConfigSettings.bq_relay_table_id
                )
            )
        )
        relays = json.loads(result[0][0])
        return relays

    def insert_relays(self, relays: list[Relay]):
        config: Settings = ConfigSettings
        return self._bq.insert_to_bigquery(
            relays,
            config.gcp_project_id,
            config.bq_dataset_id,
            config.bq_relay_table_id,
        )

    def update_relays(
        self, dataset_id: str, relays: list[Relay]
    ) -> Union[RowIterator, _EmptyRowIterator, None]:
        query = RelaySQL.update_relays(dataset_id, relays)
        return self._bq.run_sql(query)


class EventService(BqService):
    def __init__(self, client) -> None:
        super().__init__(client)

    def insert_events(self, events):
        config: Settings = ConfigSettings
        return self._bq.insert_to_bigquery(
            events,
            config.gcp_project_id,
            config.bq_dataset_id,
            config.bq_event_table_id,
        )
