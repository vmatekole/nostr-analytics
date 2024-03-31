from google.api_core.exceptions import ClientError
from google.cloud import bigquery

from utils import logger


class Bq:
    def __init__(self, client: bigquery.Client) -> None:
        self._client = client

    def run_sql(
        self,
        query,
        parameters=None,
    ) -> None:
        logger.debug(f'SQL: {query}')
        job_config = bigquery.QueryJobConfig()

        query_job: bigquery.QueryJob = self._client.query(query, job_config=job_config)
        try:
            return query_job.result()
        except ClientError as e:
            logger.error(f'Bigquery ERROR(#uyu7j): {e}')
