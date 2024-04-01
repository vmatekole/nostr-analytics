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
    def update_relays(relays: list[Relay]):
        for relay in relays:
            query: str = f"""
                UPDATE relay
                SET relay_name = {relay.relay_name},
                SET country_code= {relay.country_code},'
                SET latitude = {relay.latitude},'
                SET longitude = {relay.relay_name},'
                SET policy.write = {relay.policy.should_read},'
                SET policy.read = {relay.policy.should_write},'
                WHERE relay_url = {relay.url} \n"""
            return query
