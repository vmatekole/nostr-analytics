from nostr.relay import Relay


class RelaySQL:
    @staticmethod
    def handle_null_str(string: str) -> str:
        return 'NULL' if not string else f'\'{string}\''

    @staticmethod
    def replace_none_with_null(query: str) -> str:
        return query.replace('None', 'NULL').replace("'None'", 'NULL')

    @staticmethod
    def insert_relays(dataset_id: str, table_id: str, relays: list[Relay]) -> str:
        relays_to_insert = [
            f'''({RelaySQL.handle_null_str(relay.relay_name)},
                {RelaySQL.handle_null_str(relay.url)},
                {RelaySQL.handle_null_str(relay.country_code)},
                {relay.latitude}, {relay.longitude}, STRUCT({relay.policy.should_read} AS read, {relay.policy.should_write} AS write))\n'''
            for relay in relays
        ]
        relays_str = ' ,'.join(relays_to_insert)

        query: str = f'''
                    INSERT INTO `{dataset_id}.{table_id}` (relay_name, relay_url, country_code, latitude, longitude, policy)\n
                    VALUES {relays_str}
                '''
        query = RelaySQL.replace_none_with_null(query)
        return query

    @staticmethod
    def select_all_from(dataset_id: str, table_id: str) -> str:
        query: str = f'''
                    SELECT CONCAT("[", STRING_AGG(TO_JSON_STRING(t), ","), "]")
                    FROM `{dataset_id}.{table_id}` t
                '''
        return query

    @staticmethod
    def update_relays(dataset_id: str, relays: list[Relay]):

        query: str = ''
        for relay in relays:
            query: str = (
                query
                + f"""
                UPDATE `{dataset_id}.relay`
                SET relay_name = {RelaySQL.handle_null_str(relay.relay_name)},
                    country_code = {RelaySQL.handle_null_str(relay.country_code)},
                    latitude = {relay.latitude},
                    longitude = {relay.longitude},
                    policy.write = {relay.policy.should_read},
                    policy.read = {relay.policy.should_write}
                WHERE relay_url = '{relay.url}'; \n\n"""
            )

        query = RelaySQL.replace_none_with_null(query)
        return query
