from time import sleep

from google.cloud import bigquery

from client.bq import Bq
from config import ConfigSettings, Settings
from models.sql import RelaySQL
from utils import logger


class BqService:
    def __init__(self, client) -> None:
        self._client = client
        self._bq = Bq(client)


class RelayService(BqService):
    def __init__(self, client) -> None:
        super().__init__(client)

    def get_relays(self):
        logger.debug(f'ConfigSettings.bq_dataset_id{ConfigSettings.bq_dataset_id}')
        result = list(
            self._bq.run_sql(
                RelaySQL.select_all_from(
                    ConfigSettings.bq_dataset_id, ConfigSettings.bq_relay_table_id
                )
            )
        )
        return result[0][0]

    def insert_relays(self, relays):
        config: Settings = ConfigSettings
        return self._bq.insert_to_bigquery(
            relays,
            config.gcp_project_id,
            config.bq_dataset_id,
            config.bq_relay_table_id,
        )

    def update_relays(self, relays):
        config: Settings = ConfigSettings
        query = RelaySQL.update_relays(relays)
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
