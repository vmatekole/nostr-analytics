import pytest
from google.cloud import bigquery


@pytest.fixture(scope='class')
def event_bq_bad_insert():
    return {
        'content': 'Sample content 2',
        'kind': 1,
    }


@pytest.fixture(scope='class')
def event_bq_insert_data_1():
    return {
        'content': 'Sample content 2',
        'pubkey': 'bf8752cc0899f447a1254b5fcbc7d18c676a665166b5541fa57b461888a9fdfe',
        'created_at': 1709145700,
        'kind': 1,
    }


@pytest.fixture(scope='class')
def event_bq_insert_data_2():
    return {
        'content': 'Sample content with tags',
        'pubkey': 'bf8752cc0899f447a1254b5fcbc7d18c676a665166b5541fa57b461888a9fdfe',
        'created_at': 1709145700,
        'kind': 1,
        'tags': [['tag6', 'tag7'], ['tag8', 'tag9', 'tag10']],
    }


# TODO: Need to review if validating expected bq schema against Pydantic object is reasonable in this way.
@pytest.fixture(scope='class')
def event_bq_schema():
    return [
        bigquery.SchemaField('content', 'STRING', 'REQUIRED', None, ()),
        bigquery.SchemaField('pubkey', 'STRING', 'REQUIRED', None, ()),
        bigquery.SchemaField('created_at', 'INTEGER', 'REQUIRED', None, ()),
        bigquery.SchemaField('added_at', 'TIMESTAMP', 'REQUIRED', None, ()),
        bigquery.SchemaField('kind', 'STRING', 'REQUIRED', None, ()),
        bigquery.SchemaField('sig', 'STRING', 'NULLABLE', None, ()),
        bigquery.SchemaField(
            'tags',
            'RECORD',
            'REPEATED',
            None,
            (
                bigquery.SchemaField('tag_id', 'STRING', 'REQUIRED', None, ()),
                bigquery.SchemaField('tag_values', 'STRING', 'REPEATED', None, ()),
            ),
            None,
        ),
    ]
