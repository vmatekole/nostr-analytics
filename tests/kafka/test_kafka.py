import time

from base.config import ConfigSettings
from base.utils import logger
from kafka.consumer import NostrConsumer
from kafka.producer import NostrProducer
from kafka.schemas import EventTopic, RelayTopic
from nostr.event import Event, EventKind

from ..nostr.fixtures import event_input_data_1, event_input_data_2, relay_obj_damus
from .fixtures import kafka_event_topic


class TestEventTopic:
    def test_kafka_event_schema(self, event_input_data_1):
        # Not the most robust test for schema alignment but is better than nothing.
        event_topic: EventTopic = EventTopic(**event_input_data_1)
        assert Event.model_validate(event_input_data_1)
        assert isinstance(event_topic, EventTopic)


class TestKafkaProducer:
    def test_serialise_key_topic(self, event_input_data_1):
        topic_name: str = 'nostr-topic-name'
        key: str = 'nostr-key'
        event_topic: EventTopic = EventTopic(**event_input_data_1)
        producer: NostrProducer = NostrProducer()

        ser_key, ser_topic = producer.serialise_key_topic(
            topic_name=topic_name, key=key, event_topic=event_topic
        )

        assert ser_key == b'nostr-key'
        assert (
            ser_topic
            == b'\x00\x00\x00\x00\x02 Sample content 7\x80\x01bf8752cc0899f447a1254b5fcbc7d18c676a665166b5541fa57b461888a9fdfe\xbe\xf7\xfb\xdd\x0c\x02\x80\x0224a3a244b546f59f09a2c2ca3278e709f5cf52f015102750b4ff75985b36beb8c52986d2274e60511e5d231cbfcd9e27493fef9e0a1cb22411d57d37ab2c8c48\x04\x04\x08tag4\x08tag5\x00\x02\x08tag6\x00\x00'
        )

    def test_produce_1_event_topic(self, mocker, event_input_data_1):
        mocker.patch.object(NostrProducer, '_delivery_report')
        try:
            nostr_producer: NostrProducer = NostrProducer(EventTopic)
            topic_name = ConfigSettings.event_kafka_topic
            event_topic: EventTopic = EventTopic(**event_input_data_1)

            nostr_producer.produce(topic_name=topic_name, topics=[event_topic])
            nostr_producer._delivery_report.assert_called_once()  # type: ignore

        except Exception:
            assert False

    def test_produce_1_relay_topic(self, relay_obj_damus, mocker, event_input_data_1):
        mocker.patch.object(NostrProducer, '_delivery_report')

        try:
            nostr_producer: NostrProducer = NostrProducer(RelayTopic)
            topic_name: str = ConfigSettings.relay_kafka_topic
            relay_topic: RelayTopic = RelayTopic(
                url=relay_obj_damus.url,
                name=relay_obj_damus.name,
                latitude=relay_obj_damus.latitude,
                longitude=relay_obj_damus.longitude,
            )

            nostr_producer.produce(topic_name=topic_name, topics=[relay_topic])
            nostr_producer._delivery_report.assert_called_once()  # type: ignore

        except Exception:
            assert False

    def test_create_event_topics(self):
        nostr_producer = NostrProducer(EventTopic)

        topics: list[EventTopic] = nostr_producer.topic_events_of_kind(
            kinds=[EventKind(3)], relay_urls=['wss://relay.damus.io'], max_events=10
        )

        assert len(topics) >= 10
        assert isinstance(topics[0], EventTopic)

    def test_create_relay_topics(self):
        nostr_producer = NostrProducer(RelayTopic)

        topics: list[RelayTopic] = nostr_producer.topic_relays(
            urls=['wss://relay.damus.io']
        )

        assert len(topics) >= 10
        assert isinstance(topics[0], RelayTopic)


class TestKafkaConsumer:
    def test_consume_1_event_topic(self):
        topic_names: list[str] = [ConfigSettings.event_kafka_topic]
        nostr_consumer: NostrConsumer = NostrConsumer(topic_names, EventTopic)

        THIRTY_SECONDS = 30
        start_time = time.time()

        logger.info(
            f'Subscribed to {topic_names} and trying for 30 secs for available topics'
        )
        # Try and capture messages over a 30 second period
        while time.time() - start_time < THIRTY_SECONDS:
            key, msg = nostr_consumer.consume()
            if msg is not None:
                logger.debug(f'key: {key} topic: {msg}')
                event_topic = EventTopic(**msg)
                assert isinstance(event_topic, EventTopic)
                break

    def test_consume_1_relay_topic(self):
        topic_names: list[str] = [ConfigSettings.relay_kafka_topic]
        nostr_consumer: NostrConsumer = NostrConsumer(topic_names, RelayTopic)

        THIRTY_SECONDS = 30
        start_time = time.time()

        logger.info(
            f'Subscribed to {topic_names} and trying for 30 secs for available topics'
        )
        # Try and capture messages over a 30 second period
        while time.time() - start_time < THIRTY_SECONDS:
            key, msg = nostr_consumer.consume()
            if msg is not None:
                logger.debug(f'key: {key} topic: {msg}')
                event_topic = RelayTopic(**msg)
                assert isinstance(event_topic, RelayTopic)
                break

    def test_consume_wrong_topic_1(self):
        topic_names: list[str] = ['not-exist']
        nostr_consumer: NostrConsumer = NostrConsumer(topic_names)

        logger.info(
            f'Subscribed to erroneous topic: {topic_names} and trying for 30 secs for available topics'
        )
        try:
            key, msg = nostr_consumer.consume()
            assert False
        except Exception:
            logger.info(f'Topic: {topic_names} correctly does not exist')
            assert True
