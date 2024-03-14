from dataclasses import dataclass
from sched import Event

# event: str = """{
# "type": "record",
# "name": "User",
# "namespace": "com.upstash",
# "fields": [
#     {"name": "name", "type": "string"},
#     {"name": "favorite_number", "type": "long"}
# ]
# }
# """


@dataclass
class EventTopic:
    type: str = 'record'
    name: str = 'User'
    namespace: str = 'com.upstash'

    def __post_init__(self) -> None:
        fields_info = fields(Event)

        self.fields = [
            {
                {'name': field.name, 'type': EventTopic.get_kafka_type(field.type)}
                for field in fields_info
            }
        ]

    @staticmethod
    def get_kafka_type(field_type) -> str:
        type_mapping = {str: 'string', int: 'long'}
        return type_mapping.get(field_type, 'STRING')
