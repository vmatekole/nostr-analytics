from typing import Type, Union

from confluent_kafka import Consumer
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringDeserializer,
)
from google.cloud import bigquery

from base.utils import logger
from kafka.schemas import EventTopic, KafkaBase, RelayTopic
from nostr.event import Event
from services.bq import BqService, EventService


class NostrConsumer(KafkaBase):
    def __init__(
        self, topic_names: list[str], schema: Union[Type[EventTopic], Type[RelayTopic]]
    ) -> None:
        super().__init__()

        self._consume = False

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

        self._bq_service = EventService(bigquery.Client())

        self._consumer.subscribe(topic_names)

    def consume(self):  # -> tuple[Any, EventTopic]:
        msg = self._consumer.poll(1.0)

        if msg is not None:
            topic = self._avro_deserializer(
                msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
            )
            if msg:
                logger.debug(f'Key {msg.key()}: Value{topic} \n')
                return msg.key(), topic
        else:
            return None, None

    def consume_events(self, bq_batch_size=10):
        bq_event_batch = []
        self._consume = True

        while self._consume:
            key, msg = self.consume()
            if msg is not None:
                event_topic = EventTopic(**msg)
                events: list[Event] = EventTopic.parse_event_from_topic([event_topic])
                bq_event_batch.append(events[0])

                batch_size = len(bq_event_batch)
                if batch_size >= bq_batch_size:
                    for start in range(0, batch_size, bq_batch_size):
                        self._bq_service.save_events(
                            bq_event_batch[start : start + bq_batch_size]
                        )

                    bq_event_batch = []

    def close(self) -> None:
        self._consume = False
        self._consumer.close()
