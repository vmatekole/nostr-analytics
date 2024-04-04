from typing import Union
from unittest import result

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
    ):
        job_config = bigquery.QueryJobConfig()

        query_job: bigquery.QueryJob = self._client.query(query, job_config=job_config)
        try:
            result: RowIterator | _EmptyRowIterator = query_job.result()
            # logger.debug(f'NUM: {list(result)[0][0]}')
            if result.num_dml_affected_rows and result.num_dml_affected_rows > 0:
                return result.num_dml_affected_rows
            elif result.total_rows > 0:
                return result
            else:
                return []
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
            err_msg = f'Errors occurred while inserting rows: {errors}'
            logger.error(err_msg)
            raise Exception(f'Errors occurred while inserting rows: {err_msg}')
        else:
            logger.info(
                f'All {len(objs)} rows of {table_ref.table_id} have been inserted successfully.'
            )
            return True
