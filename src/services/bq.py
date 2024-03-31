from time import sleep

from google.cloud import bigquery

from client.bq import Bq
from config import ConfigSettings
from models.sql import RelaySQL
from utils import logger


class RelayService:
    def __init__(self, client) -> None:
        self._client = client
        self._bq = Bq(client)

    def get_relays(self):
        logger.debug(f'ConfigSettings.bq_dataset_id{ConfigSettings.bq_dataset_id}')
        result = list(
            self._bq.run_sql(RelaySQL.select_relays(ConfigSettings.bq_dataset_id))
        )
        return result

    def update_relays(self, relays):
        pass
