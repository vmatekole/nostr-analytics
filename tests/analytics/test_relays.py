import pytest

from base.config import ConfigSettings
from services.analytics import Analytics

from ..nostr.fixtures import relay_seed_urls
from .fixtures import expected_min_num_relays_10


class TestAnalyticsRelay:
    @pytest.mark.skipif(
        ConfigSettings.test_without_internet,
        reason='Internet-requiring tests are disabled',
    )
    def test_discover_relays(self, relay_seed_urls: list[str]):
        analytics: Analytics = Analytics()

        relays: set[str] = analytics.discover_relays(
            relay_seed_urls,
            100,
        )

        assert len(relays) >= 100
