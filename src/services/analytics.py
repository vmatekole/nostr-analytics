import json
import random
import time
from typing import Set

from base.config import ConfigSettings
from base.utils import logger
from nostr.event import EventKind
from nostr.filter import Filter, Filters
from nostr.message_pool import EventMessage
from nostr.relay_manager import RelayManager


class Analytics:
    def __init__(self) -> None:
        self._relay_manager = RelayManager()
        self._found_relays: set[str] = set()

    def close(self) -> None:
        self._relay_manager.close_all_relay_connections()

    def discover_relays(
        self, relay_seeds: list[str], min_relays_to_find: int = 10
    ) -> Set[str]:
        start_time: float = time.time()
        filters = Filters(initlist=[Filter(kinds=[EventKind.CONTACTS])])
        MAX_RELAYS: int = 20

        if len(relay_seeds) > MAX_RELAYS:
            raise Exception('#fgnj288: Max seeds is 20')

        for relay in relay_seeds:
            self._relay_manager.add_relay(relay)

        self._relay_manager.add_subscription_on_all_relays(id='foo', filters=filters)
        time.sleep(1.25)

        while len(self._found_relays) < min_relays_to_find:
            if (
                self._relay_manager.message_pool.has_events()
            ):  # Find better way of getting events
                event_msg: EventMessage = self._relay_manager.message_pool.get_event()
                logger.debug(f'Checking {event_msg.url}: {event_msg.event.content}')

                if (
                    event_msg.event.content == ''
                ):  # if the relay doesn't have a  follow list try the next one
                    continue

                try:
                    json_decoded: str = event_msg.event.content.replace(
                        '\"', '"'
                    )  # Sometimes we get double-encode json strings
                    discovered_relays = json.loads(json_decoded)
                except json.JSONDecodeError:
                    logger.exception(
                        f'Couldn\'t parse contact list of node {event_msg.url}'
                    )
                    continue

                for url, relay in discovered_relays.items():
                    self._found_relays.add(url)
            else:
                self._relay_manager.remove_all_relays()  # if we have gotten contact list of currently connected relays. Close current connecions
                for relay in random.sample(
                    list(self._found_relays), ConfigSettings.max_connected_relays
                ):
                    self._relay_manager.add_relay(url=relay)
                self._relay_manager.add_subscription_on_all_relays(
                    'foo', filters=filters
                )

                # TODO find better why of handling latency in connections
                time.sleep(2)

        total: float = time.time() - start_time
        logger.info(f'Discovered {self._found_relays} relays  took {total}s')

        # Cleanup
        self.close()
        return self._found_relays
