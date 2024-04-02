from config import ConfigSettings
from models.nostr.relay import Relay


class RelaySQL:
    @staticmethod
    def select_all_from(dataset_id: str, table_id: str) -> str:
        query: str = f'''
                    SELECT CONCAT("[", STRING_AGG(TO_JSON_STRING(t), ","), "]")
                    FROM `{dataset_id}.{table_id}` t
                '''
        return query

    @staticmethod
    def update_relays(dataset_id: str, relays: list[Relay]):
        for relay in relays:
            query: str = f"""
                UPDATE `{dataset_id}.relay`
                SET relay_name = '{relay.relay_name}',
                    country_code = '{relay.country_code}',
                    latitude = {relay.latitude},
                    longitude = {relay.longitude},
                    policy.write = {relay.policy.should_read},
                    policy.read = {relay.policy.should_write}
                WHERE relay_url = '{relay.url}' \n\n"""
            query = query.replace("'None'", 'NULL').replace('None', 'NULL')
            return query
