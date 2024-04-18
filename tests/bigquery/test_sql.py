import pytest

from base.config import ConfigSettings, Settings
from base.utils import normalise_string
from bigquery.sql import RelaySQL
from nostr.relay import Relay

from .fixtures import discovered_relays


class TestSQL:
    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_update_relays_sql(self, discovered_relays: list[Relay]):

        ConfigSettings.relay_refresh_ip_geo_relay_info = True
        config: Settings = ConfigSettings

        query = RelaySQL.update_relays(config.bq_dataset_id, [discovered_relays[0]])

        assert normalise_string(query) == normalise_string(
            '''UPDATE `test_event.relay`
                            SET name = NULL,
                            country_code= 'USA',
                            latitude = 37.78035,
                            longitude = -122.39059,
                            policy.write = True,
                            policy.read = True
                            WHERE url = 'wss://relay.damus.io';
            '''
        )

        ConfigSettings.relay_refresh_ip_geo_relay_info = False

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_insert_relays_sql(self, discovered_relays):
        config: Settings = ConfigSettings
        query = RelaySQL.insert_relays(
            config.bq_dataset_id, config.bq_relay_table_id, discovered_relays
        )

        assert normalise_string(query) == normalise_string(
            '''
            INSERT INTO `test_event.relay` (name, url, country_code, latitude, longitude, policy)
            VALUES (NULL, 'wss://relay.damus.io', 'USA', 37.78035, -122.39059, STRUCT(True AS read, True AS write)),
                   (NULL, 'wss://nostr.wine', 'USA', 37.78035, -122.39059, STRUCT(True AS read, True AS write)),
                   (NULL, 'wss://nostr.t-rg.ws', 'LUX', 49.79022, 6.08557, STRUCT(True AS read, True AS write))
        '''
        )
