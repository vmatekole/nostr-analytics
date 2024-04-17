import uuid
from dataclasses import asdict
from typing import Type, Union

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)
from rich import print

from base.utils import logger
from kafka.schemas import KafkaBase
from nostr.event import Event, EventKind
from nostr.relay import Relay
from services.analytics import Analytics

from .schemas import EventTopic, RelayTopic


class NostrProducer(KafkaBase):
    def __init__(
        self, topic_name: str, schema: Union[Type[EventTopic], Type[RelayTopic]]
    ) -> None:
        super().__init__()

        self._stream_on = False
        self._string_serializer = StringSerializer('utf_8')
        self._topic_name: str = topic_name

        self._producer = Producer(  # type: ignore
            {
                'bootstrap.servers': self._config.kafka_url,
                'sasl.mechanism': 'SCRAM-SHA-256',
                'security.protocol': 'SASL_SSL',
                'sasl.username': self._config.kafka_user,
                'sasl.password': self._config.kafka_pass,
            }
        )

        self._avro_serializer = AvroSerializer(
            schema_registry_client=self._schema_registry_client,
            schema_str=schema.avro_schema(),
        )

    def serialise_key_topic(self, topic_name: str, key: str, topic):
        key = self._string_serializer(key)
        mesg = self._avro_serializer(
            asdict(topic),
            SerializationContext(topic=topic_name, field=MessageField.VALUE),
        )
        return key, mesg

    def _delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def produce(self, topics: Union[list[RelayTopic], list[EventTopic]]):
        for e in topics:
            key, ser_event_topic = self.serialise_key_topic(
                self._topic_name, str(uuid.uuid4()), e
            )
            self._producer.produce(
                topic=self._topic_name,
                key=key,
                value=ser_event_topic,
                on_delivery=self._delivery_report,
            )
        self._producer.flush()

    def discover_relays(
        self, urls: list[str], min_relays_to_find: int = 10
    ) -> list[RelayTopic]:
        a: Analytics = self._a

        relays: list[Relay] = a.discover_relays(urls, min_relays_to_find)
        topics: list[RelayTopic] = [
            RelayTopic(
                url=r.url,
                name=r.name,
                country_code=r.country_code,
                latitude=r.latitude,
                longitude=r.longitude,
            )
            for r in relays
        ]

        a.close()
        return topics

    def event_topics_of_kind(
        self, kinds: list[EventKind], relay_urls: list[str], batch_size: int = 1
    ) -> list[RelayTopic]:
        a: Analytics = self._a

        events: list[Event] = a.events_of_kind(
            kinds=kinds, relay_urls=relay_urls, max_events=batch_size
        )

        topics: list[EventTopic] = [
            EventTopic(
                pubkey=e.pubkey,
                created_at=e.created_at,
                kind=e.kind,
                sig=e.sig,
                content=e.content,
                tags=e.tags,
            )
            for e in events
        ]

        return topics

    def stream_events(self, kinds: list[EventKind], relay_urls: list[str]):
        self._stream_on = True
        while self._stream_on:
            topics: list[RelayTopic] = self.event_topics_of_kind(kinds, relay_urls)
            self.produce(topics)

    def close(self):
        self._stream_on = False
