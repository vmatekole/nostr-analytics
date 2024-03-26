from dataclasses import asdict

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)

from models.base import KafkaBase

from .schemas import EventTopic


class NostrProducer(KafkaBase):
    def __init__(self) -> None:
        super().__init__()
        self._avro_serializer = AvroSerializer(
            schema_registry_client=self._schema_registry_client,
            schema_str=EventTopic.avro_schema(),
        )

        self._string_serializer = StringSerializer('utf_8')

        self._producer = Producer(  # type: ignore
            {
                'bootstrap.servers': self._config.kafka_url,
                'sasl.mechanism': 'SCRAM-SHA-256',
                'security.protocol': 'SASL_SSL',
                'sasl.username': self._config.kafka_user,
                'sasl.password': self._config.kafka_pass,
            }
        )

    def serialise_key_topic(self, topic_name: str, key: str, event_topic: EventTopic):
        key = self._string_serializer(key)
        mesg = self._avro_serializer(
            asdict(event_topic),
            SerializationContext(topic=topic_name, field=MessageField.VALUE),
        )
        return key, mesg

    def _delivery_report(self, err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    def produce(self, topic_name: str, key: str, event_topic: EventTopic):
        key, ser_event_topic = self.serialise_key_topic(topic_name, key, event_topic)
        self._producer.produce(
            topic=topic_name,
            key=key,
            value=ser_event_topic,
            on_delivery=self._delivery_report,
        )
        self._producer.flush()
