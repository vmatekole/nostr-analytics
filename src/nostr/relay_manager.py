import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock

from google.cloud import bigquery
from pydantic import ValidationError

from base.utils import logger
from services import bq

from .event import Event
from .filter import Filters
from .message_pool import MessagePool
from .relay import Relay, RelayPolicy, RelayProxyConnectionConfig
from .request import Request


class RelayException(Exception):
    pass


@dataclass
class RelayManager:
    def __post_init__(self):
        client = bigquery.Client()
        self._bq_service = bq.RelayService(client)
        self.relays: dict[str, Relay] = {}
        self.message_pool: MessagePool = MessagePool()
        self.lock: Lock = Lock()
        self.executor = ThreadPoolExecutor(
            max_workers=100
        )  # Adjust the max_workers as needed

    def add_relay(
        self,
        url: str,
        policy: RelayPolicy = RelayPolicy(),
        reconnect: bool = True,
        ssl_options=None,
        proxy_config: RelayProxyConnectionConfig = None,
    ):
        try:
            relay = Relay(
                url, policy=policy, message_pool=self.message_pool, reconnect=reconnect
            )
        except ValidationError as e:
            logger.exception(f'#kjhkjh8: Invalid relay url {e}')
            raise

        with self.lock:
            self.relays[url] = relay

        self.executor.submit(relay.connect)
        if reconnect:  # Normal operation: resilient long-running connections
            self.executor.submit(relay.queue_worker)
        else:  # For verification of relay only
            self.executor.submit(relay.verify_relay)

        time.sleep(1)

    def remove_relay(self, url: str):
        with self.lock:
            if url in self.relays:
                relay: Relay = self.relays.pop(url)
                relay.close()

    def remove_all_relays(self):
        with self.lock:
            for relay in list(self.relays.items()):
                relay: Relay = self.relays.pop(relay[0])
                relay.close()

    def add_subscription_on_relay(self, url: str, id: str, filters: Filters):
        with self.lock:
            if url in self.relays:
                relay: Relay = self.relays[url]
                if not relay.policy.should_read:
                    raise RelayException(
                        f'Could not send request: {url} is not configured to read from'
                    )
                relay.add_subscription(id, filters)
                request = Request(id, filters)
                relay.publish(request.to_message())
            else:
                raise RelayException(f'Invalid relay url: no connection to {url}')

    def add_subscription_on_all_relays(self, id: str, filters: Filters):
        with self.lock:
            for relay in self.relays.values():
                if relay.policy.should_read:
                    relay.add_subscription(id, filters)
                    request = Request(id, filters)
                    relay.publish(request.to_message())

    def close_subscription_on_relay(self, url: str, id: str):
        with self.lock:
            if url in self.relays:
                relay: Relay = self.relays[url]
                relay.close_subscription(id)
                relay.publish(json.dumps(['CLOSE', id]))
            else:
                raise RelayException(f'Invalid relay url: no connection to {url}')

    def close_subscription_on_all_relays(self, id: str):
        with self.lock:
            for relay in self.relays.values():
                relay.close_subscription(id)
                relay.publish(json.dumps(['CLOSE', id]))

    def close_all_relay_connections(self):
        with self.lock:
            for url in self.relays:
                relay: Relay = self.relays[url]
                relay.close()

    def publish_event(self, event: Event):
        """Verifies that the Event is publishable before submitting it to relays"""
        if event.signature is None:
            raise RelayException(f'Could not publish {event.id}: must be signed')

        if not event.verify():
            raise RelayException(
                f'Could not publish {event.id}: failed to verify signature {event.signature}'
            )

        with self.lock:
            for relay in self.relays.values():
                if relay.policy.should_write:
                    relay.publish(event.to_message())
