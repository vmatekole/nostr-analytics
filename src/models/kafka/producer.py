from confluent_kafka import Producer  # type: ignore
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, StringSerializer

from config import Configuration

from .schemas import EventTopic


class NostrProducer:
    def __init__(self) -> None:
        self._config: Configuration = Configuration.get_config_of_env_vars()

        self._schema_registry_client = SchemaRegistryClient(
            conf={
                'url': self._config.KAFKA_SCHEMA_URL,
                'basic.auth.user.info': self._config.KAFKA_SCHEMA_AUTH_TOKEN,
            }
        )

        self._avro_serializer = AvroSerializer(
            schema_registry_client=self._schema_registry_client,
            schema_str=EventTopic.get_kafka_schema(),
        )

        self._string_serializer = StringSerializer('utf_8')

        self._producer = Producer(  # type: ignore
            {
                'bootstrap.servers': self._config.KAFKA_URL,
                'sasl.mechanism': 'SCRAM-SHA-256',
                'security.protocol': 'SASL_SSL',
                'sasl.username': self._config.KAFKA_USER,
                'sasl.password': self._config.KAFKA_PASS,
            }
        )

    def produce(self, topic: str, key: str, value: EventTopic):
        self._producer.produce(
            topic=topic,
            key=self._string_serializer(key),
            value=self._avro_serializer(
                value, SerializationContext(topic=topic, field=MessageField.VALUE)
            ),
        )
        self._producer.flush()
