from dataclasses import dataclass

from confluent_kafka.schema_registry import SchemaRegistryClient
from dataclasses_avroschema import AvroModel

from base.config import ConfigSettings, Settings


class KafkaBase:
    def __init__(self) -> None:
        self._config: Settings = ConfigSettings

        self._config
        self._schema_registry_client = SchemaRegistryClient(
            conf={
                'url': self._config.kafka_schema_url,
                'basic.auth.user.info': self._config.kafka_schema_auth_token,
            }
        )


@dataclass
class EventTopic(AvroModel):
    pubkey: str
    created_at: int
    kind: int
    sig: str
    content: str = None
    tags: list[list[str]] = None


@dataclass
class RelayTopic(AvroModel):
    url: str
    name: str = None
    latitude: float = None
    longitude: float = None
