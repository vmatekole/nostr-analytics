import json
import random
import socket
import time
from ast import Set
from collections import namedtuple
from dataclasses import asdict, dataclass

import requests

from config import ConfigSettings
from models.nostr.event import EventKind
from models.nostr.filter import Filter, Filters
from models.nostr.message_pool import EventMessage
from models.nostr.relay_manager import RelayManager
from utils import logger


class Analytics:
    RelayMeta = namedtuple(typename='RelayMeta', field_names='url read write')

    def __init__(self) -> None:
        self._relay_manager = RelayManager()
        self._found_relays: set = set()
        self._config: Settings = Settings()

    def discover_relays(
        self, relay_seeds: list[str], min_relays_to_find: int = 5000
    ) -> Set:
        start_time = time.time()
        prev_connected_relays: set = set()
        MAX_RELAYS: int = 20
        filters = Filters(initlist=[Filter(kinds=[EventKind.CONTACTS])])
        # ["REQ","foo",{"kind": 3}]
        if len(relay_seeds) > min_relays_to_find:
            raise Exception(
                '#fg2898: Default limit is 10 but number of seeds is more, reduce num seeds or increase limit'
            )
        if len(relay_seeds) > MAX_RELAYS:
            raise Exception('#fgnj288: Max seeds is 20')

        for relay in relay_seeds:
            self._relay_manager.add_relay(relay)

        self._relay_manager.add_subscription_on_all_relays(id='foo', filters=filters)
        time.sleep(1.25)
        prev_connected_relays = set(self._relay_manager.relays.keys())
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

                # self._relay_manager.remove_all_relays() # We don't want to connect to too many relays at once
                for url, relay in discovered_relays.items():
                    # relay_meta = self.RelayMeta(url, relay['read'], relay['write'])
                    self._found_relays.add(url)

                logger.debug(f'Already SEEN: {len(self._found_relays)}')
                logger.debug(f'Current relays: {len(self._relay_manager.relays)}')
            else:
                self._relay_manager.remove_all_relays()
                for relay in random.sample(list(self._found_relays), 10):
                    self._relay_manager.add_relay(relay)
                self._relay_manager.add_subscription_on_all_relays(
                    'foo', filters=filters
                )
                # TODO find better why of handling latency in connections
                time.sleep(2)

        total = start_time - time.time()
        logger.info(f'Discovering {min_relays_to_find} relays  took {total}s')
        logger.info(f'Discovered {self._found_relays} relays  took {total}s')
        return self._found_relays
