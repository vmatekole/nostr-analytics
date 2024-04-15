from typing import Type, Union

from confluent_kafka import Consumer
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringDeserializer,
)

from kafka.schemas import EventTopic, KafkaBase, RelayTopic


class NostrConsumer(KafkaBase):
    def __init__(
        self, topic_names: list[str], schema: Union[Type[EventTopic], Type[RelayTopic]]
    ) -> None:
        super().__init__()

        self._string_serializer = StringDeserializer('utf_8')
        self._avro_deserializer = AvroDeserializer(
            schema_registry_client=self._schema_registry_client,
            schema_str=schema.avro_schema(),
        )

        self._consumer = Consumer(  # type: ignore
            {
                'bootstrap.servers': self._config.kafka_url,
                'sasl.mechanism': 'SCRAM-SHA-256',
                'security.protocol': 'SASL_SSL',
                'sasl.username': self._config.kafka_user,
                'sasl.password': self._config.kafka_pass,
                'group.id': self._config.kafka_consumer_group,
                'auto.offset.reset': 'earliest',
            }
        )
        self._consumer.subscribe(topic_names)

    def consume(self):  # -> tuple[Any, EventTopic]:
        msg = self._consumer.poll(1.0)

        if msg is not None:
            topic = self._avro_deserializer(
                msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
            )
            if msg:
                print(f'Key {msg.key()}: Value{topic} \n')
                return msg.key(), topic
        else:
            return None, None

    def close(self) -> None:
        self._consumer.close()

    # def __del__(self) -> None:
    #     self._consumer.close()
