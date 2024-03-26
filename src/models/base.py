# from abc import ABC
from typing import Any, List

from confluent_kafka.schema_registry import SchemaRegistryClient
from google.cloud import bigquery
from pydantic import BaseModel

from config import Configuration
from utils import logger


class KafkaBase:
    def __init__(self) -> None:
        self._config: Configuration = Configuration.get_config_of_env_vars()

        self._schema_registry_client = SchemaRegistryClient(
            conf={
                'url': self._config.KAFKA_SCHEMA_URL,
                'basic.auth.user.info': self._config.KAFKA_SCHEMA_AUTH_TOKEN,
            }
        )


class BaseBQModel(BaseModel):
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
        ]

        return schema

    @staticmethod
    def persist_to_bigquery(
        events: List['BaseBQModel'], dataset_id: str, table_id: str
    ):
        client = bigquery.Client()

        table_ref: bigquery.TableReference = client.dataset(dataset_id).table(table_id)
        table = bigquery.Table(table_ref, schema=BaseBQModel.bq_schema())

        rows_to_insert = []
        for event in events:
            row: dict[str, Any] = event.model_dump()
            rows_to_insert.append(row)

        # Insert rows into BigQuery table
        errors = client.insert_rows(table, rows_to_insert)
        if errors:
            logger.error(f'Errors occurred while inserting rows: {errors}')
        else:
            logger.error('All rows have been inserted successfully.')
            return True
