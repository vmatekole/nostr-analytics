import pytest
from google.cloud import bigquery


@pytest.fixture(scope='class')
def event_bq_insert_data_1():
    return {
        'content': 'Sample content 2',
        'pubkey': 'bf8752cc0899f447a1254b5fcbc7d18c676a665166b5541fa57b461888a9fdfe',
        'created_at': 1709145700,
        'kind': 1,
    }


@pytest.fixture(scope='class')
def event_bq_schema():
    return [
        bigquery.SchemaField('content', 'STRING', 'NULLABLE', None, None, (), None),
        bigquery.SchemaField('pubkey', 'STRING', 'NOT NULL', None, None, (), None),
        bigquery.SchemaField('created_at', 'INT64', 'NOT NULL', None, None, (), None),
        bigquery.SchemaField('kind', 'INT64', 'NOT NULL', None, None, (), None),
        bigquery.SchemaField('sig', 'STRING', 'NULLABLE', None, None, (), None),
        bigquery.SchemaField('tags', 'STRING', 'REPEATED', None, None, (), None),
    ]
