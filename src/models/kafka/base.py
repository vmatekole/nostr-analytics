from confluent_kafka.schema_registry import SchemaRegistryClient

from config import Configuration


class KafkaBase:
    def __init__(self) -> None:
        self._config: Configuration = Configuration.get_config_of_env_vars()

        self._schema_registry_client = SchemaRegistryClient(
            conf={
                'url': self._config.KAFKA_SCHEMA_URL,
                'basic.auth.user.info': self._config.KAFKA_SCHEMA_AUTH_TOKEN,
            }
        )
