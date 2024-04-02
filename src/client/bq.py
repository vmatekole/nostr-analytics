from typing import Union

from google.api_core.exceptions import ClientError
from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator, _EmptyRowIterator

from base.utils import logger


class Bq:
    def __init__(self, client: bigquery.Client) -> None:
        self._client = client

    def run_sql(
        self,
        query,
    ) -> Union[RowIterator, _EmptyRowIterator, None]:
        job_config = bigquery.QueryJobConfig()

        query_job: bigquery.QueryJob = self._client.query(query, job_config=job_config)
        try:
            return query_job.result()
        except ClientError as e:
            logger.error(f'Bigquery ERROR(#uyu7j): {e}')

    def insert_to_bigquery(
        self, objs: list[any], project_id: str, dataset_id: str, table_id: str
    ):
        client = self._client

        table_ref: bigquery.TableReference = bigquery.TableReference(
            bigquery.DatasetReference(project_id, dataset_id), table_id
        )

        table = client.get_table(table_ref)

        rows_to_insert = []
        for obj in objs:
            row: dict[str, Any] = obj.bq_dump()
            rows_to_insert.append(row)

        # Insert rows into BigQuery table
        errors = client.insert_rows_json(table, rows_to_insert)
        if errors:
            raise Exception(f'Errors occurred while inserting rows: {errors}')
        else:
            logger.debug('All rows have been inserted successfully.')
            return True
