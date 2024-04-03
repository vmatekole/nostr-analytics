import re

from base.config import ConfigSettings, Settings
from base.utils import logger
from bigquery.sql import RelaySQL
from nostr.relay import Relay

from .fixtures import discovered_relays


class TestSQL:
    def normalise_string(self, query: str):
        return re.sub(r'\s+', '', query)

    def test_update_relays_sql(self, discovered_relays: list[Relay]):
        config: Settings = ConfigSettings

        query = RelaySQL.update_relays(config.bq_dataset_id, [discovered_relays[0]])

        assert self.normalise_string(query) == self.normalise_string(
            '''UPDATE `test_event.relay`
                            SET relay_name = NULL,
                            country_code= 'USA',
                            latitude = 37.78035,
                            longitude = -122.39059,
                            policy.write = True,
                            policy.read = True
                            WHERE relay_url = 'wss://relay.damus.io'
            '''
        )

    def test_insert_relays_sql(self, discovered_relays):
        config: Settings = ConfigSettings
        query = RelaySQL.insert_relays(
            config.bq_dataset_id, config.bq_relay_table_id, discovered_relays
        )

        assert self.normalise_string(query) == self.normalise_string(
            '''
            INSERT INTO `test_event.relay` (relay_name, relay_url, country_code, latitude, longitude, policy)
            VALUES ('None', 'wss://relay.damus.io', 'USA', 37.78035, -122.39059, STRUCT(True AS read, True AS write)),
                   ('None', 'wss://nostr.wine', 'USA', 37.78035, -122.39059, STRUCT(True AS read, True AS write)),
                   ('None', 'wss://nostr.t-rg.ws', 'LUX', 49.79022, 6.08557, STRUCT(True AS read, True AS write))
        '''
        )
