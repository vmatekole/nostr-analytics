import time
from unittest.mock import Mock

from google.cloud import bigquery

from base.config import ConfigSettings
from base.utils import logger
from kafka.consumer import NostrConsumer
from kafka.producer import NostrProducer
from kafka.schemas import EventTopic, RelayTopic
from nostr.event import Event, EventKind
from nostr.relay import Relay
from services import bq


class TestRelayAnalytics:
    def test_producing_relay_topics(self, mocker):
        mocker.patch.object(NostrProducer, '_delivery_report')

        nostr_producer = NostrProducer(RelayTopic)

        try:
            topics: list[RelayTopic] = nostr_producer.topic_relays(
                urls=['wss://relay.damus.io']
            )
            topics = topics[:10]
            nostr_producer.produce(ConfigSettings.relay_kafka_topic, topics)
        except Exception:
            assert False

        nostr_producer._delivery_report.assert_called()  # type: ignore
        assert len(topics) >= 10


class TestEventAnalytics:
    def test_producing_event_topics(self, mocker):

        mocker.patch.object(NostrProducer, '_delivery_report')

        nostr_producer = NostrProducer(EventTopic)

        try:
            topics: list[EventTopic] = nostr_producer.topic_events_of_kind(
                kinds=[EventKind(EventKind.CONTACTS)],
                relay_urls=['wss://relay.damus.io'],
                max_events=10,
            )
            topics = topics[:10]

            nostr_producer.produce(ConfigSettings.event_kafka_topic, topics)
        except Exception:
            assert False

        nostr_producer._delivery_report.assert_called()  # type: ignore
        assert len(topics) >= 10

    def test_producing_and_save_events(self, mocker):
        topic_names: list[str] = [ConfigSettings.event_kafka_topic]
        bq_service = bq.EventService(bigquery.Client())
        MAX_EVENTS = 10

        mocker.patch.object(NostrProducer, '_delivery_report')

        nostr_producer = NostrProducer(topic_names[0], EventTopic)
        nostr_consumer = NostrConsumer(topic_names, EventTopic)

        try:
            topics: list[EventTopic] = nostr_producer.topic_events_of_kind(
                kinds=[EventKind(EventKind.CONTACTS)],
                relay_urls=['wss://relay.damus.io'],
                max_events=MAX_EVENTS,
            )

            nostr_producer.produce(topics)
            nostr_consumer.consume()

            num_events = 0
            event_topics = []

            while num_events <= MAX_EVENTS:
                key, msg = nostr_consumer.consume()
                if msg is not None:
                    logger.debug(f'key: {key} topic: {msg}')
                    event_topic = EventTopic(**msg)
                    event_topics.append(event_topic)
                    assert isinstance(event_topic, EventTopic)
                    num_events += 1
            events: list[Event] = EventTopic.parse_event_from_topic(event_topics)
            bq_service.save_events(events)

        except Exception:
            assert False

        nostr_producer._delivery_report.assert_called()  # type: ignore
        assert num_events >= MAX_EVENTS
