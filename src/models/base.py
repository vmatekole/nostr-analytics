# from abc import ABC
from typing import Any, List

from confluent_kafka.schema_registry import SchemaRegistryClient
from google.cloud import bigquery
from h11 import Event
from pydantic import BaseModel

from config import Settings
from utils import logger


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

    @staticmethod
    def persist_to_bigquery(
        events: List['ModelBase'], project_id: str, dataset_id: str, table_id: str
    ):
        client = bigquery.Client()

        table_ref: bigquery.TableReference = bigquery.TableReference(
            bigquery.DatasetReference(project_id, dataset_id), table_id
        )
        # bigquery.Table(table_ref, BaseBQModel.bq_schema())
        table = client.get_table(table_ref)

        rows_to_insert = []
        for event in events:
            row: dict[str, Any] = event.bq_dump()
            rows_to_insert.append(row)

        logger.debug(f'TABLE: {table}')
        logger.debug(f'rows: {rows_to_insert}')
        # Insert rows into BigQuery table
        errors = client.insert_rows_json(table, rows_to_insert)
        if errors:
            raise Exception(f'Errors occurred while inserting rows: {errors}')
        else:
            logger.debug('All rows have been inserted successfully.')
            return True
