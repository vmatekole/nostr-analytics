import json
from typing import Any, Union

from google.cloud.bigquery.table import Row, RowIterator

from base.config import ConfigSettings, Settings
from base.utils import logger
from bigquery.sql import EventsSQL, RelaySQL
from client.bq import Bq
from nostr.event import Event
from nostr.relay import Relay, RelayPolicy


class BqService:
    def __init__(self, client) -> None:
        self._client = client
        self._bq = Bq(client)


class RelayService(BqService):
    def __init__(self, client) -> None:
        super().__init__(client)

    def _parse_relays(self, result) -> list[Relay]:
        if not result[0][0]:
            return []

        relays = json.loads(
            result[0][0]
        )  # for RelaySQL.select_all_from returns a single row of a json array of relays is returned

        relay_objs: list[Relay] = []
        for r in relays:
            relay_objs.append(
                Relay(
                    url=r['url'],
                    policy=RelayPolicy(r['policy']['read'], r['policy']['write']),
                    name=r['name'],
                    country_code=r['country_code'],
                    latitude=r['latitude'],
                    longitude=r['longitude'],
                )
            )

        return relay_objs

    def get_relays(self) -> list[Relay]:
        result = list(
            self._bq.run_sql(
                RelaySQL.select_all_from(
                    ConfigSettings.bq_dataset_id, ConfigSettings.bq_relay_table_id
                )
            )
        )

        relays: list[Relay] = self._parse_relays(result) if result else []
        return relays

    def save_relays(self, relays: list[Relay]):
        query: str = RelaySQL.insert_relays(
            ConfigSettings.bq_dataset_id, ConfigSettings.bq_relay_table_id, relays
        )
        return self._bq.run_sql(query)

    def update_relays(
        self, dataset_id: str, relays: list[Relay]
    ) -> Union[RowIterator, None]:
        query = RelaySQL.update_relays(dataset_id, relays)
        return self._bq.run_sql(query)

    def upsert_relays(
        self, dataset_id: str, relays: list[Relay]
    ) -> Union[RowIterator, None]:
        if not self._relays:
            self._relays: list[Relay] = self.get_relays()


class EventService(BqService):
    def __init__(self, client) -> None:
        super().__init__(client)

    def save_events(self, events):
        config: Settings = ConfigSettings
        return self._bq.insert_to_bigquery(
            events,
            config.gcp_project_id,
            config.bq_dataset_id,
            config.bq_event_table_id,
        )
