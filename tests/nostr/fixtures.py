from typing import Literal

import pytest


@pytest.fixture(scope='class')
def event_input_data_1():
    return {
        'sig': '24a3a244b546f59f09a2c2ca3278e709f5cf52f015102750b4ff75985b36beb8c52986d2274e60511e5d231cbfcd9e27493fef9e0a1cb22411d57d37ab2c8c48',
        'content': 'Sample content 7',
        'pubkey': 'bf8752cc0899f447a1254b5fcbc7d18c676a665166b5541fa57b461888a9fdfe',
        'created_at': 1709145567,
        'kind': 1,
        'tags': [['tag4', 'tag5'], ['tag6']],
    }


@pytest.fixture(scope='class')
def expected_bytes_for_input_data_1():
    return (
        b'[0,"Sample content'
        b' 1","bf8752cc0899f447a1254b5fcbc7d18c676a665166b5541fa57b461888a9fdfe",1709145567,1,[["tag4","tag5"],["tag6"]]]'
    )


@pytest.fixture(scope='class')
def event_input_data_2():
    return {
        'content': 'Sample content 2',
        'pubkey': 'bf8752cc0899f447a1254b5fcbc7d18c676a665166b5541fa57b461888a9fdfe',
        'created_at': 1709145700,
        'kind': 1,
    }


@pytest.fixture(scope='class')
def event_input_data_3():
    return '["EVENT","sub_1",{"id":"45d2688ae616cc1ed0b26d5be242fa43ec29ed49729dc8c0c6ed9b6a22eddea2","pubkey":"e25a8b2051022a08f97d267d4b99ddfc500a0bfe149a5f671e46f72e9ea36ec9","created_at":1700454780,"kind":30078,"tags":[["d","snort"]],"content":"4lqbPvAsTY5JWL9/8MyTR80S9/vTU/vRj/8LkR14Qhmgd0FLqpBhg4idKHih/m9UmSzyaxgxsA3t0aMKaUKKcRLm7xV0nE4xAxCCroGjGyOFgPgfju127wRWaYzLEghoKl4+su4Fhq6b7cl/+EQK0CLXEzZG2LowHrwA00DDkmNkI0gU4csLwVItx18efjhaHTyKgLA5uWdsfePUUfJvOSJxHpo2EXTeM9YdBXHoFQTnEXoq8K/sI1Muku83NHgqR6A81H364bnrV2HJLd8rQoblRSRitTfr40iEdr1jq49mippehh01fteLOSheCIJvvRNw7jRK0gN4c+sBl2aVinmregqQPMzPyhKV67Oxsti887plr80RThJHXXJW7moBrvCr8Zc1QP81d2yrwerMsTwpJI9aQMmPzNrdVD/JwNsaIxmQgFCqCFBYJWtHKeDBfmm6XGcozSWhvfreEHRSYguo75bTBI+f7N6lG0lnPl+WMzfgkabKpouK/vhATFUX7hELxiUvs2rT++nqT7T8MaD5uuV44wMorjMaNpaI5ZEV976pqPfI3SUH46WvFPDsfZaguTRtdBGK+RQ8bYCOyxboCmeYNv0n3K9oaXaO0l2b0WWQvTxOWFfKuWTmHZuNkEl3IOZyLdBVpGglGxmpzUSp7vtXWZzEOS/byKreYAJqEa865n3mNi2rs7NdJ8WEkvzrfD8BVevIL4ypKJEngh6TuYT+MwZ4irAJ36/6vsasH6Ax131DFia+s74P7NI4wkO3kQQHGPs+bnH4TM6+dcrzU2U647RZ+pqzCugPjM87nM9Gz7Sxay8u9Mu605P+LAQ6/wrt4h2m4Tmsye7mae5RujoaLRClLoOwfKN7cOEwLudTyrSPbuSRpS8EBo6v?iv=YT1wowyulhlpeXnbrCfpvQ==","sig":"24a3a244b546f59f09a2c2ca3278e709f5cf52f015102750b4ff75985b36beb8c52986d2274e60511e5d231cbfcd9e27493fef9e0a1cb22411d57d37ab2c8c48"}]'


@pytest.fixture(scope='class')
def expected_sig_for_input_data_1():
    return '583123f70e2e0e650e87dc34e01530179907997a3e159c8169a80917ac2cabf0'


@pytest.fixture(scope='class')
def expected_event_obj_3():
    return {
        'pubkey': 'e25a8b2051022a08f97d267d4b99ddfc500a0bfe149a5f671e46f72e9ea36ec9',
        'created_at': 1700454780,
        'kind': 30078,
        'tags': [['d', 'snort']],
        'content': '4lqbPvAsTY5JWL9/8MyTR80S9/vTU/vRj/8LkR14Qhmgd0FLqpBhg4idKHih/m9UmSzyaxgxsA3t0aMKaUKKcRLm7xV0nE4xAxCCroGjGyOFgPgfju127wRWaYzLEghoKl4+su4Fhq6b7cl/+EQK0CLXEzZG2LowHrwA00DDkmNkI0gU4csLwVItx18efjhaHTyKgLA5uWdsfePUUfJvOSJxHpo2EXTeM9YdBXHoFQTnEXoq8K/sI1Muku83NHgqR6A81H364bnrV2HJLd8rQoblRSRitTfr40iEdr1jq49mippehh01fteLOSheCIJvvRNw7jRK0gN4c+sBl2aVinmregqQPMzPyhKV67Oxsti887plr80RThJHXXJW7moBrvCr8Zc1QP81d2yrwerMsTwpJI9aQMmPzNrdVD/JwNsaIxmQgFCqCFBYJWtHKeDBfmm6XGcozSWhvfreEHRSYguo75bTBI+f7N6lG0lnPl+WMzfgkabKpouK/vhATFUX7hELxiUvs2rT++nqT7T8MaD5uuV44wMorjMaNpaI5ZEV976pqPfI3SUH46WvFPDsfZaguTRtdBGK+RQ8bYCOyxboCmeYNv0n3K9oaXaO0l2b0WWQvTxOWFfKuWTmHZuNkEl3IOZyLdBVpGglGxmpzUSp7vtXWZzEOS/byKreYAJqEa865n3mNi2rs7NdJ8WEkvzrfD8BVevIL4ypKJEngh6TuYT+MwZ4irAJ36/6vsasH6Ax131DFia+s74P7NI4wkO3kQQHGPs+bnH4TM6+dcrzU2U647RZ+pqzCugPjM87nM9Gz7Sxay8u9Mu605P+LAQ6/wrt4h2m4Tmsye7mae5RujoaLRClLoOwfKN7cOEwLudTyrSPbuSRpS8EBo6v?iv=YT1wowyulhlpeXnbrCfpvQ==',
        'sig': '24a3a244b546f59f09a2c2ca3278e709f5cf52f015102750b4ff75985b36beb8c52986d2274e60511e5d231cbfcd9e27493fef9e0a1cb22411d57d37ab2c8c48',
    }


@pytest.fixture(scope='class')
def reliable_relay_url() -> Literal['wss://relay.damus.io']:
    return 'wss://relay.damus.io'


@pytest.fixture(scope='class')
def reliable_relay_policy() -> dict[str, bool]:
    return {'read': True, 'write': True}


@pytest.fixture(scope='class')
def relay_seed_urls() -> list[str]:
    return ['wss://relay.damus.io', 'wss://relay.nostr.net']


@pytest.fixture(scope='class')
def expected_min_num_relays_10() -> int:
    return 10


@pytest.fixture(scope='class')
def kafka_event_topic() -> str:
    return '{"type": "record", "name": "EventTopic", "fields": [{"name": "content", "type": "string"}, {"name": "pubkey", "type": "string"}, {"name": "created_at", "type": "long"}, {"name": "kind", "type": "long"}, {"name": "sig", "type": "string"}, {"name": "tags", "type": {"type": "array", "items": {"type": "array", "items": "string", "name": "tag"}, "name": "tag"}}]}'
