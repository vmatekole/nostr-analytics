from typing import Type, Union

from confluent_kafka import Consumer
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringDeserializer,
)
from google.cloud import bigquery

from base.config import ConfigSettings
from base.utils import logger
from kafka.producer import NostrProducer
from kafka.schemas import EventTopic, KafkaBase, RelayTopic
from nostr.event import Event
from nostr.relay import Relay
from services.bq import BqService, EventService, RelayService


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

        self._bq_event_service = EventService(bigquery.Client())
        self._bq_relay_service = RelayService(bigquery.Client())

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
                        self._bq_event_service.save_events(
                            bq_event_batch[start : start + bq_batch_size]
                        )

                    bq_event_batch.clear()

    def consume_relays(self, bq_batch_size=10):
        bq_relay_batch: list[Relay] = []
        self._consume = True

        while self._consume:
            key, msg = self.consume()
            if msg is not None:
                relay_topic = RelayTopic(**msg)
                relays: list[Event] = RelayTopic.parse_relay_from_topic([relay_topic])
                bq_relay_batch.append(relays[0])

            batch_size = len(bq_relay_batch)
            if batch_size >= bq_batch_size:
                for start in range(0, batch_size, bq_batch_size):
                    self._bq_relay_service.save_relays(
                        relays[start : start + bq_batch_size]
                    )

                bq_relay_batch.clear()

    def close(self) -> None:
        self._consume = False
        self._consumer.close()
