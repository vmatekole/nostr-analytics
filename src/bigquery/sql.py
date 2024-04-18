import sqlglot
import sqlglot.errors

from base.utils import logger
from nostr.event import Event
from nostr.relay import Relay

#  TODO Replace this withh sqlglot


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
            f'''({RelaySQL.handle_null_str(relay.name)},
                {RelaySQL.handle_null_str(relay.url)},
                {RelaySQL.handle_null_str(relay.country_code)},
                {relay.latitude}, {relay.longitude}, STRUCT({relay.policy.should_read} AS read, {relay.policy.should_write} AS write))\n'''
            for relay in relays
        ]
        relays_str = ' ,'.join(relays_to_insert)

        query: str = f'''
                    INSERT INTO `{dataset_id}.{table_id}` (name, url, country_code, latitude, longitude, policy)\n
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
                SET name = {RelaySQL.handle_null_str(relay.name)},
                    country_code = {RelaySQL.handle_null_str(relay.country_code)},
                    latitude = {relay.latitude},
                    longitude = {relay.longitude},
                    policy.write = {relay.policy.should_read},
                    policy.read = {relay.policy.should_write},
                    modified_at = CURRENT_TIMESTAMP()
                WHERE url = '{relay.url}'; \n\n"""
            )

        query = RelaySQL.replace_none_with_null(query)
        return query


class EventsSQL:
    @staticmethod
    def insert_events(dataset_id: str, table_id: str, events: list[Event]) -> str:
        events_to_insert = []

        for e in events:
            content = e.content.replace("'", '')  # TODO need to preserve quotes
            content = content.strip().replace('\n', '\\n')

            events_to_insert.append(
                f'''('{content}','{e.pub_key}',{int(e.kind)},'{e.sig}',{e.created_at})\n'''
            )
        relays_str = ' ,'.join(events_to_insert)

        query: str = f'''
                    INSERT INTO {dataset_id}.{table_id} (content, pubkey, kind, sig, created_at)\n
                    VALUES {relays_str}
                '''
        try:
            query = sqlglot.transpile(query)
        except sqlglot.errors.ParseError as e:
            logger.exception(e)

        return query
