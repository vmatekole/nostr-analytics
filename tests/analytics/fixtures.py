import pytest


@pytest.fixture(scope='class')
def expected_min_num_relays_10() -> int:
    return 10
