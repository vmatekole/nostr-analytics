from bigquery.sql import RelaySQL
from nostr.relay import Relay

from .fixtures import discovered_relays


class TestSQL:
    def normalise_string(self, query: str):
        return ''.split(query)

    def test_select_relays_sql(self):
        dataset_id = 'test_events'
        table_id = 'relay'
        result = RelaySQL.select_all_from(dataset_id, table_id)
        assert (
            result
            == 'SELECT relay_name, relay_url, country_code, latitude, longitude, policy.read, policy.writeFROM `test_events.relay`'
        )

    def test_update_relays_sql(self, discovered_relays: list[Relay]):

        query = RelaySQL.update_relays([discovered_relays[0]])

        assert self.normalise_string(query) == self.normalise_string(
            """UPDATE relay
                            SET relay_name = None,
                            SET country_code= USA,'
                            SET latitude = 37.78035,'
                            SET longitude = None,'
                            SET policy.write = True,'
                            SET policy.read = True,'
                            WHERE relay_url = wss://relay.damus.io"""
        )
