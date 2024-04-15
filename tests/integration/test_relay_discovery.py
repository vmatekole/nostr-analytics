from unittest.mock import Mock

from base.config import ConfigSettings
from kafka.producer import NostrProducer
from kafka.schemas import EventTopic, RelayTopic
from nostr.event import EventKind
from nostr.relay import Relay


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
                kinds=[EventKind(3)], relay_urls=['wss://relay.damus.io'], max_events=10
            )
            topics = topics[:10]

            nostr_producer.produce(ConfigSettings.event_kafka_topic, topics)
        except Exception:
            assert False

        nostr_producer._delivery_report.assert_called()  # type: ignore
        assert len(topics) >= 10
