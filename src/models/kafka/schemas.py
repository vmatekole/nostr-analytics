import stat
from ast import List
from dataclasses import dataclass, fields
from operator import concat

from models.nostr.event import Event, EventKind


@dataclass
class EventTopic:
    event: Event

    def __post_init__(self) -> None:
        self.type: str = 'record'
        self.name: str = 'Event'
        self.namespace: str = 'com.upstash'

        self.fields_info = fields(Event)

        self.fields = [
            {'name': field.name, 'type': EventTopic.get_kafka_type(field.type)}
            for field in self.fields_info
        ]

    def __str__(self) -> str:
        fields = [
            f'{{"name": "{field.name}", "type": "{EventTopic.get_kafka_type(field.type)}"}}'
            for field in self.fields_info
            if EventTopic.get_kafka_type(field.type) != 'unknown'
        ]

        fields.append(
            str(
                {
                    'name': 'tags',
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': {'type': 'map', 'values': 'string'},
                    },
                }
            ).replace("'", '"')
        )
        fields_str: str = ', '.join(fields)

        return f'{{"type": "{self.type}", "name": "{self.name}", "namespace": "{self.namespace}", "fields": [{fields_str}]}}'

    @staticmethod
    def get_kafka_type(field_type) -> str:
        type_mapping = {str: 'string', int: 'long'}
        return type_mapping.get(field_type, 'unknown')

    @staticmethod
    def get_kafka_schema() -> str:
        event_dict = {
            'pubkey': 'e25a8b2051022a08f97d267d4b99ddfc500a0bfe149a5f671e46f72e9ea36ec9',
            'created_at': 1700454780,
            'kind': 30078,
            'tags': [['d', 'snort']],
            'content': '4lqbPvAsTY5JWL9/8MyTR80S9/vTU/vRj/8LkR14Qhmgd0FLqpBhg4idKHih/m9UmSzyaxgxsA3t0aMKaUKKcRLm7xV0nE4xAxCCroGjGyOFgPgfju127wRWaYzLEghoKl4+su4Fhq6b7cl/+EQK0CLXEzZG2LowHrwA00DDkmNkI0gU4csLwVItx18efjhaHTyKgLA5uWdsfePUUfJvOSJxHpo2EXTeM9YdBXHoFQTnEXoq8K/sI1Muku83NHgqR6A81H364bnrV2HJLd8rQoblRSRitTfr40iEdr1jq49mippehh01fteLOSheCIJvvRNw7jRK0gN4c+sBl2aVinmregqQPMzPyhKV67Oxsti887plr80RThJHXXJW7moBrvCr8Zc1QP81d2yrwerMsTwpJI9aQMmPzNrdVD/JwNsaIxmQgFCqCFBYJWtHKeDBfmm6XGcozSWhvfreEHRSYguo75bTBI+f7N6lG0lnPl+WMzfgkabKpouK/vhATFUX7hELxiUvs2rT++nqT7T8MaD5uuV44wMorjMaNpaI5ZEV976pqPfI3SUH46WvFPDsfZaguTRtdBGK+RQ8bYCOyxboCmeYNv0n3K9oaXaO0l2b0WWQvTxOWFfKuWTmHZuNkEl3IOZyLdBVpGglGxmpzUSp7vtXWZzEOS/byKreYAJqEa865n3mNi2rs7NdJ8WEkvzrfD8BVevIL4ypKJEngh6TuYT+MwZ4irAJ36/6vsasH6Ax131DFia+s74P7NI4wkO3kQQHGPs+bnH4TM6+dcrzU2U647RZ+pqzCugPjM87nM9Gz7Sxay8u9Mu605P+LAQ6/wrt4h2m4Tmsye7mae5RujoaLRClLoOwfKN7cOEwLudTyrSPbuSRpS8EBo6v?iv=YT1wowyulhlpeXnbrCfpvQ==',
            'sig': '24a3a244b546f59f09a2c2ca3278e709f5cf52f015102750b4ff75985b36beb8c52986d2274e60511e5d231cbfcd9e27493fef9e0a1cb22411d57d37ab2c8c48',
        }
        event: EventTopic = EventTopic(Event(**event_dict))
        return str(event)
