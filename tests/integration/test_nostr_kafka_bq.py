import pydantic
import pytest
from google.cloud import bigquery

from base.config import ConfigSettings
from base.utils import logger
from kafka.consumer import NostrConsumer
from kafka.producer import NostrProducer
from kafka.schemas import EventTopic, RelayTopic
from nostr.event import Event, EventKind
from services import bq


class TestRelayAnalytics:
    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_producing_relay_topics(self, mocker):
        mocker.patch.object(NostrProducer, '_delivery_report')

        nostr_producer = NostrProducer(ConfigSettings.relay_kafka_topic, RelayTopic)

        try:
            topics: list[RelayTopic] = nostr_producer.discover_relays(
                urls=['wss://relay.damus.io']
            )
            topics = topics[:10]
            nostr_producer.produce(ConfigSettings.relay_kafka_topic, topics)
        except Exception:
            assert False

        nostr_producer._delivery_report.assert_called()  # type: ignore
        assert len(topics) >= 10


class TestEventAnalytics:
    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_producing_event_topics(self, mocker):
        mocker.patch.object(NostrProducer, '_delivery_report')

        nostr_producer = NostrProducer(ConfigSettings.event_kafka_topic, EventTopic)

        try:
            topics: list[EventTopic] = nostr_producer.event_topics_of_kind(
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

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_producing_and_saving_events(self, mocker):
        topic_names: list[str] = [ConfigSettings.event_kafka_topic]
        bq_service = bq.EventService(bigquery.Client())
        MAX_EVENTS = 100

        mocker.patch.object(NostrProducer, '_delivery_report')

        nostr_producer = NostrProducer(topic_names[0], EventTopic)
        nostr_consumer = NostrConsumer(topic_names, EventTopic)

        try:
            topics: list[EventTopic] = nostr_producer.event_topics_of_kind(
                kinds=[
                    EventKind(EventKind.TEXT_NOTE),
                    EventKind.REACTIONS,
                    EventKind(EventKind.LONG_FORM_CONTENT),
                ],
                relay_urls=['wss://relay.damus.io', 'wss://nostr.wine'],
                max_events=MAX_EVENTS,
            )

            nostr_producer.produce(topics)

            num_events = 0
            event_topics = []

            while num_events <= MAX_EVENTS:
                key, msg = nostr_consumer.consume()
                if msg is not None:
                    event_topic = EventTopic(**msg)
                    event_topics.append(event_topic)
                    assert isinstance(event_topic, EventTopic)
                    num_events += 1
            events: list[Event] = EventTopic.parse_event_from_topic(event_topics)
            step = 50
            for start in range(0, len(events), step):
                assert bq_service.save_events(events[start : start + step])

        except Exception:
            assert False

        nostr_producer._delivery_report.assert_called()  # type: ignore
        assert num_events >= MAX_EVENTS

    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_producing_and_saving_relays(self, mocker):
        topic_names: list[str] = [ConfigSettings.relay_kafka_topic]
        bq_service = bq.RelayService(bigquery.Client())
        MAX_RELAYS = 10

        mocker.patch.object(NostrProducer, '_delivery_report')

        nostr_producer = NostrProducer(topic_names[0], RelayTopic)
        nostr_consumer = NostrConsumer(topic_names, RelayTopic)

        try:
            topics: list[EventTopic] = nostr_producer.discover_relays(
                urls=['wss://relay.damus.io', 'wss://nostr.wine'],
                min_relays_to_find=MAX_RELAYS,
            )

            nostr_producer.produce(topics)

            num_relays = 0
            relay_topics = []

            while num_relays <= MAX_RELAYS:
                key, msg = nostr_consumer.consume()
                if msg is not None:
                    relay_topic = RelayTopic(**msg)
                    relay_topics.append(relay_topic)
                    assert isinstance(relay_topic, RelayTopic)
                    num_relays += 1
            relays: list[Event] = RelayTopic.parse_relay_from_topic(relay_topics)

            step = 50
            for start in range(0, len(relays), step):
                assert bq_service.save_relays(relays[start : start + step])

        except pydantic.ValidationError:
            # Pydantic validation error can be thrown for erroneous relay urls
            assert True
        except Exception as e:
            logger.debug(e)
            # assert True

        nostr_producer._delivery_report.assert_called()  # type: ignore

    # def test_stream_events(self, mocker):
    #     topic_names: list[str] = [ConfigSettings.event_kafka_topic]

    #     # mocker.patch.object(NostrProducer, '_delivery_report')

    #     nostr_producer = NostrProducer(topic_names[0], EventTopic)

    #     nostr_producer.stream_events(kinds=[EventKind(EventKind.TEXT_NOTE), EventKind.REACTIONS, EventKind(EventKind.LONG_FORM_CONTENT)],
    #                                  relay_urls=['wss://relay.damus.io', 'wss://nostr.wine'])

    # def test_consume_events(self, mocker):
    #     topic_names: list[str] = [ConfigSettings.event_kafka_topic]

    #     # mocker.patch.object(NostrProducer, '_delivery_report')

    #     nostr_consumer = NostrConsumer(topic_names, EventTopic)

    #     nostr_consumer.consume_events()
