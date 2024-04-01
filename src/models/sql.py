from models.nostr.relay import Relay


class RelaySQL:
    @staticmethod
    def select_relays(dataset_id: str) -> str:
        query: str = (
            f'SELECT relay_name, relay_url, country_code, latitude, longitude, policy.read, policy.write'
            f'FROM `{dataset_id}.relay`'
        )
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
