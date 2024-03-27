from typing import List

from google.cloud import bigquery

from models.base import ModelBase
from utils import logger


class BqUtils:
    @staticmethod
    def persist_to_bigquery(
        events: List[ModelBase], project_id: str, dataset_id: str, table_id: str
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
