from models.kafka.producer import NostrProducer
from models.kafka.schemas import EventTopic
from models.nostr.event import Event

from ..nostr.fixtures import event_input_data_1, event_input_data_2
from .fixtures import kafka_event_topic


class TestEventTopic:
    def test_kafka_event_schema(self, kafka_event_topic: str):
        print(EventTopic.generate_dataclass())
        print(Event)
        assert EventTopic.avro_schema() == kafka_event_topic


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
            == b'\x00\x00\x00\x00\x02 Sample content 1\x80\x01bf8752cc0899f447a1254b5fcbc7d18c676a665166b5541fa57b461888a9fdfe\xbe\xf7\xfb\xdd\x0c\x02\x80\x0224a3a244b546f59f09a2c2ca3278e709f5cf52f015102750b4ff75985b36beb8c52986d2274e60511e5d231cbfcd9e27493fef9e0a1cb22411d57d37ab2c8c48\x04\x04\x08tag4\x08tag5\x00\x02\x08tag6\x00\x00'
        )

    def test_producer_1(self, mocker, event_input_data_1):
        mocker.patch.object(NostrProducer, '_delivery_report')

        try:
            nostr_producer: NostrProducer = NostrProducer()
            topic_name = 'nostr'
            event_topic: EventTopic = EventTopic(**event_input_data_1)
            key: str = 'nostr-topic-key'

            nostr_producer.produce(
                topic_name=topic_name, key=key, event_topic=event_topic
            )
            nostr_producer._delivery_report.assert_called_once()

            assert True
        except Exception:
            assert False
