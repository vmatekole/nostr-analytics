import json
import time
import uuid
from typing import Set, Union

from google.cloud import bigquery
from pydantic import ValidationError

from base.utils import clean_url, logger
from nostr.event import Event, EventKind
from nostr.filter import Filter, Filters
from nostr.message_pool import EventMessage
from nostr.relay import Relay
from nostr.relay_manager import RelayManager
from services import bq


class Analytics:
    def __init__(self) -> None:
        self._relay_manager = RelayManager()
        self._relay_urls_to_try: set[str] = set()
        self._bq_service = bq.RelayService(bigquery.Client())
        self._discovered_relays: list[Relay] = self._bq_service.get_relays()

    def __del__(self):
        self.close()

    def _connect_to_relays(self, urls: list[str], filters: Filters):
        for url in urls:
            self._relay_manager.add_relay(url)
            self._relay_manager.add_subscription_on_relay(
                url, id=str(uuid.uuid4()), filters=filters
            )

    def _upsert_relay_info(self, relays: list[Relay]):
        bq_service = self._bq_service

        urls: Set[str] = set([relay.url for relay in relays]) - set(
            [relay.url for relay in self._discovered_relays]
        )

        relays_to_save: list[Relay] = [r for r in relays if r.url in urls]
        if len(relays_to_save) > 0:
            self._discovered_relays.extend(
                relays_to_save
            )  # TODO: Comeback to this as it isn't clear as to whether policy is clients or servers ability
            bq_service.save_relays(relays_to_save)

    def _relay_discovered(self, url: str):
        self._relay_urls_to_try.remove(url)
        self._relay_manager.remove_relay(url)
        self._upsert_relay_info(Relay(url=url))

    def _create_relays(self, urls: list[str]):
        relays: list[Relay] = []
        for url in urls:
            try:
                relay = Relay(url)
                relays.append(relay)
            except Exception as e:
                logger.debug(f'#kjhkjh8: Invalid relay url {e}')
        return relays

    def _add_relays_to_bq(self, urls: list[str]):
        relays: list[Relay] | None = self._create_relays(urls)
        self._upsert_relay_info(relays=relays)

    def _add_relay_for_discovery(self, url: str, filters: Filters):
        try:
            self._relay_manager.add_relay(url=url)
        except Exception as e:
            logger.debug(f'#kjhh7 {e}')
            return

        self._connect_to_relays([url], filters)

    def close(self) -> None:
        self._relay_manager.close_all_relay_connections()

        """ Discover follow lists of relays
        """

    def discover_relays(
        self, relay_seeds: list[str], min_relays_to_find: int = 10
    ) -> list[Relay]:
        start_time: float = time.time()
        filters = Filters(initlist=[Filter(kinds=[EventKind.CONTACTS])])
        MAX_RELAYS: int = 20

        if len(relay_seeds) > MAX_RELAYS:
            raise Exception('#fgnj288: Max seeds is 20')

        for relay_url in relay_seeds:
            self._add_relay_for_discovery(relay_url, filters)

        time.sleep(1.25)

        urls: set[str] = set()
        while len(urls) < min_relays_to_find:

            if self._relay_manager.message_pool.has_events():
                event_msg: EventMessage = self._relay_manager.message_pool.get_event()
                logger.debug(f'Got response:{event_msg.url}')

                if (
                    not event_msg.event.content == ''
                ):  # if the relay doesn't have a follow list try the next one
                    try:
                        json_decoded: str = event_msg.event.content.replace(
                            '\"', '"'
                        )  # Sometimes we get double-encode json strings
                        discovered_relays = json.loads(json_decoded)

                        if getattr(
                            discovered_relays, 'items', None
                        ):  # valid json array is not guaranteed
                            for relay in discovered_relays.items():
                                urls.add(clean_url(relay[0]))

                            urls.add(clean_url(event_msg.url))

                        else:
                            logger.debug(
                                f'{event_msg.url} not a valid json array {discovered_relays}'
                            )
                    except json.JSONDecodeError:
                        logger.exception(
                            f'Couldn\'t parse contact list of node {event_msg.url}'
                        )
                        continue
                else:
                    logger.debug(
                        f'{event_msg.url} has no follow list {event_msg.event}'
                    )

            # TODO find better why of handling latency in connections
            logger.debug(f'Found: {len(urls)}')
            time.sleep(0.2)

        total: float = time.time() - start_time
        relays: Union[list[Relay], None] = self._create_relays(list(urls))

        logger.info(f'Discovered {len(urls)} relays  took {total}s')

        # Cleanup
        self.close()

        return relays

    def events_of_kind(
        self, kinds: list[EventKind], relay_urls: list[str], max_events=-1
    ) -> Union[list[Event], None]:
        filters = Filters(initlist=[Filter(kinds=kinds)])
        self._connect_to_relays(relay_urls, filters)

        num_of_events = 0

        events: list[Event] = []

        try:
            while True:
                if self._relay_manager.message_pool.has_events():
                    event_msg: EventMessage = (
                        self._relay_manager.message_pool.get_event()
                    )
                    events.append(event_msg.event)
                    num_of_events += 1
                else:
                    logger.info(f'Num of events {num_of_events}')
                    if not max_events == -1 and num_of_events >= max_events:
                        break
            self.close()

            return events
        except Exception as e:
            logger.exception(f'#jj88: {e}')
