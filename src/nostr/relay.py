import json
import socket
import time
from dataclasses import dataclass
from queue import Queue
from threading import Lock
from typing import Annotated, Optional

import requests
from pydantic import BaseModel, ConfigDict, UrlConstraints, ValidationError
from pydantic_core import Url
from websocket import WebSocketApp, WebSocketException

from base.config import ConfigSettings, Settings
from base.utils import clean_url, logger

from .event import Event
from .filter import Filters
from .message_pool import MessagePool
from .message_type import RelayMessageType
from .subscription import Subscription

WssUrl = Annotated[
    Url,
    UrlConstraints(max_length=2083, allowed_schemes=['wss', 'ws']),
]


class UrlValidation(BaseModel):
    url: WssUrl


@dataclass
class RelayPolicy:
    model_config = ConfigDict(arbitrary_types_allowed=True)

    should_read: bool = True
    should_write: bool = False

    def to_json_object(self) -> dict[str, bool]:
        return {'read': self.should_read, 'write': self.should_write}


@dataclass
class RelayProxyConnectionConfig:
    model_config = ConfigDict(arbitrary_types_allowed=True)

    host: Optional[str] = None
    port: Optional[int] = None
    type: Optional[str] = None


@dataclass
class Relay:
    url: str
    policy: RelayPolicy = RelayPolicy()
    message_pool: MessagePool = None
    name: str = None
    ssl_options: Optional[dict] = None
    proxy_config: RelayProxyConnectionConfig = None
    country_code: str = None
    latitude: float = None
    longitude: float = None
    connected: bool = False
    reconnect: bool = False
    ws: WebSocketApp = None

    def _validate_url(self, url: str):
        UrlValidation(url=url)

    def __post_init__(self):
        try:
            url = clean_url(self.url)

            url = f'ws://{url}' if ('wss://' not in url and 'ws://' not in url) else url
            self._validate_url(url)
        except ValidationError:
            raise

        self.queue = Queue()
        self.subscriptions: dict[str, Subscription] = {}
        self.num_sent_events: int = 0
        self.connected: bool = False
        self.error_counter: int = 0
        self.error_threshold: int = 0
        self.terminate_q_worker = False

        if (
            self.message_pool
        ):  # TODO: A bit hacky. For some analytics purposes we don't want to connect to the relay.
            self.lock: Lock = Lock()
            self.ws: WebSocketApp = WebSocketApp(
                self.url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )

        if ConfigSettings.relay_refresh_ip_geo_relay_info:
            self.refresh_geo_ip_info()

    def _on_open(self, class_obj):
        self.connected = True

    def _on_close(self, class_obj, status_code, message):
        self.connected = False
        self.terminate_q_worker = True

    def _on_message(self, class_obj, message: str):
        self.message_pool.add_message(message, self.url)

    def _on_error(self, class_obj, error):
        self.connected = False
        self.error_counter += 1
        if self.error_threshold and self.error_counter > self.error_threshold:
            logger.error(f'Unable to connect to ${self.url}. Disconnecting!')
        else:
            self.check_reconnect()

    def _is_valid_message(self, message: str) -> bool:
        message = message.strip('\n')
        if not message or message[0] != '[' or message[-1] != ']':
            return False

        message_json = json.loads(message)
        message_type = message_json[0]
        if not RelayMessageType.is_valid(message_type):
            return False
        if message_type == RelayMessageType.EVENT:
            if not len(message_json) == 3:
                return False

            subscription_id = message_json[1]
            with self.lock:
                if subscription_id not in self.subscriptions:
                    return False

            e = message_json[2]
            event = Event(
                e['content'],
                e['pubkey'],
                e['created_at'],
                e['kind'],
                e['tags'],
                e['sig'],
            )
            if not event.verify():
                return False

            with self.lock:
                subscription = self.subscriptions[subscription_id]

            if subscription.filters and not subscription.filters.match(event):
                return False

        return True

    def connect(self):
        try:
            self.ws.run_forever(
                sslopt=self.ssl_options,
                http_proxy_host=self.proxy_config.host
                if self.proxy_config is not None
                else None,
                http_proxy_port=self.proxy_config.port
                if self.proxy_config is not None
                else None,
                proxy_type=self.proxy_config.type
                if self.proxy_config is not None
                else None,
            )
        except Exception as e:
            logger.exception(f'#kik9: {e}  url:{self.url}')
            self.close()

    def close(self):
        self.ws.close()

    def check_reconnect(self):
        try:
            self.close()
        except:
            pass
        self.connected = False
        if self.reconnect:
            time.sleep(1)
            self.connect()

    def publish(self, message: str):
        self.queue.put(message)

    def queue_worker(self):
        while True:
            if self.connected and not self.terminate_q_worker:
                message = self.queue.get()
                try:
                    self.ws.send(message)
                    self.num_sent_events += 1
                except:
                    self.queue.put(message)
            elif not self.connected and self.terminate_q_worker:
                break
            else:
                time.sleep(0.1)

    def add_subscription(self, id, filters: Filters):
        with self.lock:
            self.subscriptions[id] = Subscription(id, filters)

    def close_subscription(self, id: str) -> None:
        with self.lock:
            self.subscriptions.pop(id, None)

    def update_subscription(self, id: str, filters: Filters) -> None:
        with self.lock:
            subscription = self.subscriptions[id]
            subscription.filters = filters

    def to_json_object(self) -> dict:
        return {
            'url': self.url,
            'policy': self.policy.to_json_object(),
            'subscriptions': [
                subscription.to_json_object()
                for subscription in self.subscriptions.values()
            ],
        }

    def to_dict(self):
        return {
            'url': self.url,
            'name': self.name or '',
            'country_code': self.country_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'policy': {
                'read': self.policy.should_read,
                'write': self.policy.should_write,
            },
        }

    def refresh_geo_ip_info(self):
        result = Relay.get_relay_geo_info([self.url.replace('wss://', '')])[0]
        self.country_code = result['country_code3']
        self.latitude = result['latitude']
        self.longitude = result['longitude']

    @staticmethod
    def get_geo_info(ip_addresses):
        config: Settings = ConfigSettings
        result = []
        for ip in ip_addresses:
            try:
                response = requests.get(
                    f'{config.ip_geolocation_url}?apiKey={config.ip_geolocation_key}&ip={ip}',
                    data=json.dumps(ip_addresses),
                    headers={'Content-Type': 'application/json'},
                )
                if response.status_code == 200:
                    result.append(response.json())
                else:
                    response.raise_for_status()
            except requests.HTTPError:
                logger.error(
                    f'Unable to call{config.ip_geolocation_url} for ip address {ip}'
                )
        return result

    @staticmethod
    def get_relay_geo_info(relays: list[str]):
        ip_addresses = []
        geo_location_info = []
        for relay_domain in relays:
            try:
                ip_address = socket.gethostbyname(relay_domain)
                ip_addresses.append(ip_address)
            except socket.gaierror:
                return None
            return Relay.get_geo_info(ip_addresses)
