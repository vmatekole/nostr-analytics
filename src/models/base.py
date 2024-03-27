from confluent_kafka.schema_registry import SchemaRegistryClient
from google.cloud import bigquery
from pydantic import BaseModel

from config import Settings


class KafkaBase:
    def __init__(self) -> None:
        self._config: Settings = Settings()

        self._config
        self._schema_registry_client = SchemaRegistryClient(
            conf={
                'url': self._config.kafka_schema_url,
                'basic.auth.user.info': self._config.kafka_schema_auth_token,
            }
        )


class ModelBase(BaseModel):
    @classmethod
    def bq_schema(cls):
        type_mapping: dict[type[str] | type[int] | type[bool], str] = {
            str: 'STRING',
            int: 'INT64',
            bool: 'BOOL',
        }

        schema: List[bigquery.SchemaField] = [
            bigquery.SchemaField(
                name,
                type_mapping.get(field.annotation, 'STRING'),
                mode=cls._get_field_mode(name, field),
            )
            for name, field in cls.model_fields.items()
            if not name == 'tags'
        ]
        schema.append(
            bigquery.SchemaField(
                'tags',
                'RECORD',
                'REPEATED',
                None,
                None,
                (
                    bigquery.SchemaField(
                        'tag', 'STRING', 'REPEATED', None, None, (), None
                    ),
                ),
                None,
            ),
        )

        return schema
