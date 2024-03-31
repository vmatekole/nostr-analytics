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


@pytest.fixture(scope='class')
def event_bq_insert_data_3():
    return {
        'id': '582d6a82dadc52d013434cacf1731dbb77b0c986573a71b2eabed26cc3b29491',
        'pubkey': 'd1d1747115d16751a97c239f46ec1703292c3b7e9988b9ebdd4ec4705b15ed44',
        'created_at': 1711878755,
        'kind': 1,
        'tags': [
            ['t', 'ArchLinixInstallBattle'],
            ['t', 'archlinixinstallbattle'],
            [
                'r',
                'https://image.nostr.build/fda28ae54660c60db9ca5146d0529d0b79eda05c194f2252733ce544f8a175d1.jpg',
            ],
            [
                'imeta',
                'url https://image.nostr.build/fda28ae54660c60db9ca5146d0529d0b79eda05c194f2252733ce544f8a175d1.jpg',
                'm image/jpeg',
                'alt Verifiable file url',
                'x 6aefdec83c48eec58e63d224c357aade3a918f39834888bb400b560ef13fb9dd',
                'size 245739',
                'dim 1920x1080',
                'blurhash i88|^ouPeoI9rWI9I9Mxn#J4$dIoa%t8o#o3jct7rYnP%2SeNZSgozW.R*xat7kVozRkWBkVkWV[%MozRjjbsAV@aeofjZ',
                'ox fda28ae54660c60db9ca5146d0529d0b79eda05c194f2252733ce544f8a175d1',
            ],
        ],
        'content': '#ArchLinixInstallBattle してる\nhttps://image.nostr.build/fda28ae54660c60db9ca5146d0529d0b79eda05c194f2252733ce544f8a175d1.jpg',
        'sig': 'e3089dde35dca03da096f46d12c977c257476773c0f55b333d6b20b19c3b28561776dac31e76d2ade511721cf7303efe0ef1fc8ff0532b511eef688c992861cc',
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
