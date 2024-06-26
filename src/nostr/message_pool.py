"""
    The basis of the code below was taken from https://github.com/jeffthibault/python-nostr with some modifications.
"""
import json
import re
from queue import Queue
from threading import Lock

from rich import print

from base.utils import clean_url, logger

from .event import Event
from .message_type import RelayMessageType


class EventMessage:
    def __init__(self, event: Event, subscription_id: str, url: str) -> None:
        self.event = event
        self.subscription_id = subscription_id
        self.url = url


class NoticeMessage:
    def __init__(self, content: str, url: str) -> None:
        self.content = content
        self.url = url


class EndOfStoredEventsMessage:
    def __init__(self, subscription_id: str, url: str) -> None:
        self.subscription_id = subscription_id
        self.url = url


class MessagePool:
    def __init__(self) -> None:
        self.events: Queue[EventMessage] = Queue()
        self.notices: Queue[NoticeMessage] = Queue()
        self.eose_notices: Queue[EndOfStoredEventsMessage] = Queue()
        self._unique_events: set = set()
        self._connected_relays: set[str] = set()
        self.lock: Lock = Lock()

    def add_message(self, message: str, url: str):
        self._process_message(message, url)

    def get_event(self) -> EventMessage:
        return self.events.get()

    def get_notice(self) -> NoticeMessage:
        return self.notices.get()

    def get_eose_notice(self):
        return self.eose_notices.get()

    def has_events(self):
        return self.events.qsize() > 0

    def has_notices(self):
        return self.notices.qsize() > 0

    def has_eose_notices(self):
        return self.eose_notices.qsize() > 0

    def _process_message(self, message: str, url: str):
        message_json = json.loads(message)
        message_type = message_json[0]
        url = clean_url(url)

        if message_type == RelayMessageType.EVENT:
            subscription_id = message_json[1]
            e = message_json[2]

            event = Event(
                content=e['content'],
                pubkey=e['pubkey'],
                created_at=e['created_at'],
                kind=e['kind'],
                tags=e['tags'],
                sig=e['sig'],
            )

            with self.lock:
                if not event.id in self._unique_events:
                    self.events.put(EventMessage(event, subscription_id, url))
                    self._unique_events.add(event.id)
        elif message_type == RelayMessageType.NOTICE:
            self.notices.put(NoticeMessage(message_json[1], url))
        elif message_type == RelayMessageType.END_OF_STORED_EVENTS:
            self.eose_notices.put(EndOfStoredEventsMessage(message_json[1], url))
