from models.sql import RelaySQL

from .fixtures import discovered_relays


class TestSQL:
    def test_update_relays_sql(self, discovered_relays):

        normalise_string = lambda s: ''.split(s)

        query = RelaySQL.update_relays([discovered_relays[0]])

        assert normalise_string(query) == normalise_string(
            """UPDATE relay
                            SET relay_name = None,
                            SET country_code= USA,'
                            SET latitude = 37.78035,'
                            SET longitude = None,'
                            SET policy.write = True,'
                            SET policy.read = True,'
                            WHERE relay_url = wss://relay.damus.io"""
        )
