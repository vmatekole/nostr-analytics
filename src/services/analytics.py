import json
import random
import time
from typing import Set

from google.cloud import bigquery

from base.config import ConfigSettings
from base.utils import logger
from nostr.event import EventKind
from nostr.filter import Filter, Filters
from nostr.message_pool import EventMessage
from nostr.relay import Relay, RelayPolicy
from nostr.relay_manager import RelayManager
from services import bq


class Analytics:
    def __init__(self) -> None:
        self._relay_manager = RelayManager()
        self._found_relays_urls: set[str] = set()
        self._bq_service = bq.RelayService(bigquery.Client())
        self._alive_relays = self._bq_service.get_relays()

        # self.discovered_relays: list[Relay] = self._bq_service.get_relays()

    def _upsert_relay_info(self, relay: Relay):
        bq_service = self._bq_service
        discovered_relay = None

        if self._alive_relays:
            for r in self._alive_relays:
                if r.url == relay.url:
                    discovered_relay = r

            # discovered_relay = next(
            #     r for r in self.discovered_relays if r.url == relay.url)

        if not discovered_relay:
            self._alive_relays.append(
                relay
            )  # TODO: Comeback to this as it isn't clear as to whether policy is clients or servers ability
            bq_service.save_relays([relay])

    def close(self) -> None:
        self._relay_manager.close_all_relay_connections()

    def discover_relays(
        self, relay_seeds: list[str], min_relays_to_find: int = 1000
    ) -> Set[str]:
        start_time: float = time.time()
        filters = Filters(initlist=[Filter(kinds=[EventKind.CONTACTS])])
        MAX_RELAYS: int = 20

        if len(relay_seeds) > MAX_RELAYS:
            raise Exception('#fgnj288: Max seeds is 20')

        for relay_url in relay_seeds:
            self._relay_manager.add_relay(relay_url)

        self._relay_manager.add_subscription_on_all_relays(id='foo', filters=filters)
        time.sleep(1.25)

        while len(self._alive_relays) < min_relays_to_find:
            if (
                self._relay_manager.message_pool.has_events()
            ):  # Find better way of getting events
                event_msg: EventMessage = self._relay_manager.message_pool.get_event()
                logger.debug(f'Got response:{event_msg.url}')

                if (
                    event_msg.event.content == ''
                ):  # if the relay doesn't have a follow list try the next one
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

                self._upsert_relay_info(Relay(url=event_msg.url))

                for url, _ in discovered_relays.items():
                    self._found_relays_urls.add(url)
            else:
                # if we have gotten contact list of currently connected relays. Close current connecions

                for url in self._relay_manager.relays:
                    self._found_relays_urls.remove(url)

                self._relay_manager.remove_all_relays()
                for url in random.sample(list(self._found_relays_urls), 100):
                    self._relay_manager.add_relay(url=url)

                self._relay_manager.add_subscription_on_all_relays(
                    'foo', filters=filters
                )

                # TODO find better why of handling latency in connections
                logger.debug(f'Attempting to connect : {self._relay_manager.relays}')
                time.sleep(2)

        total: float = time.time() - start_time
        logger.info(f'Discovered {self._alive_relays} relays  took {total}s')

        # Cleanup
        self.close()

        return self._alive_relays
