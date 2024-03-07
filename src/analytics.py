import json
import logging
from ast import Set
from collections import namedtuple
from dataclasses import asdict, dataclass
from itertools import islice
from os import write

from models.nostr.event import EventKind
from models.nostr.filter import Filter, Filters
from models.nostr.message_pool import EventMessage
from models.nostr.relay_manager import RelayManager

logger = logging.getLogger()

logging.getLogger().setLevel(logging.DEBUG)

FORMAT = 'VICTOR %(message)s'
logging.basicConfig(
    level=logging.DEBUG,
    format=FORMAT,
    datefmt='[%X]',
    handlers=[
        logging.StreamHandler().setLevel(logging.DEBUG),
        logging.FileHandler('logs/debug11.log'),
    ],
)


class Analytics:
    RelayMeta = namedtuple(typename='RelayMeta', field_names='url read write')

    def __init__(self) -> None:
        self._relay_manager = RelayManager()
        self._seen_relays: set = set()

    def discover_relays(self, relay_seeds: list[str], min: int = 1000) -> Set:
        already_connected: set = set()
        MAX_RELAYS: int = 20
        filters = Filters(initlist=[Filter(kinds=[EventKind.CONTACTS])])
        # ["REQ","foo",{"kind": 3}]
        if len(relay_seeds) > min:
            raise Exception(
                '#fg2898: Default limit is 10 but number of seeds is more, reduce num seeds or increase limit'
            )
        if len(relay_seeds) > MAX_RELAYS:
            raise Exception('#fgnj288: Max seeds is 20')

        for relay in relay_seeds:
            self._relay_manager.add_relay(relay)

        self._relay_manager.add_subscription_on_all_relays(id='foo', filters=filters)

        while True:
            if self._relay_manager.message_pool.has_events():
                event_msg: EventMessage = self._relay_manager.message_pool.get_event()
                logger.debug(f'Checking {event_msg.url}: {event_msg.event.content}')
                for relay in self._relay_manager.relays:
                    already_connected.add(relay)
                self._relay_manager.remove_all_relays()  # we don't want to be connected to too many relays at a time

                if (
                    event_msg.event.content == ''
                ):  # if the relay doesn't have a  follow list try the next one
                    continue

                discovered_relays = json.loads(event_msg.event.content)
                for url, relay in discovered_relays.items():
                    relay_meta = self.RelayMeta(url, relay['read'], relay['write'])
                    self._seen_relays.add(relay_meta)

                if len(self._seen_relays) < min:
                    for relay in self._seen_relays:
                        found_relay = filter(
                            lambda connected_relay: relay.url == connected_relay.url,
                            already_connected,
                        )
                        if not found_relay:
                            self._relay_manager.add_relay(relay)
                    logger.debug(f'Already SEEN: {self._seen_relays}')
                    logger.debug(f'Current relays: {self._relay_manager.relays}')
                else:
                    break
        return self._seen_relays
