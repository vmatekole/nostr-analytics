import json
import time
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from hashlib import sha256
from typing import List

from .message_type import ClientMessageType


class EventKind(IntEnum):
    SET_METADATA = 0
    TEXT_NOTE = 1
    RECOMMEND_RELAY = 2
    CONTACTS = 3
    ENCRYPTED_DIRECT_MESSAGE = 4
    DELETE = 5


@dataclass
class Event:
    content: str = field(metadata={'text': 'nostr txt content'})
    public_key: str = field(
        metadata={
            'public key': '32-bytes lowercase hex-encoded public key of the event creator'
        }
    )
    created_at: int = field(metadata={'seconds': 'unix timestamp in seconds'})
    kind: int = EventKind.TEXT_NOTE
    signature: str = field(
        default=None,
        metadata={
            'event signature': '64-bytes lowercase hex of the signature of the sha256 hash of the serialized event data, which is the same as the "id" field'
        },
    )
    tags: List[List[str]] = field(
        default_factory=list, metadata={'content tag': 'arbitrary string'}
    )

    """Initialises 'content' and 'created_at' fields post initialisation
    """

    def __post_init__(self) -> None:
        if self.content is not None and not isinstance(self.content, str):
            # DMs initialize content to None but all other kinds should pass in a str
            raise TypeError("Argument 'content' must be of type str")

        if self.created_at is None:
            self.created_at = int(time.time())

    """Serialises Event obj to a byte string

    Returns:
        bytes: Serialized Event obj
    """

    @staticmethod
    def serialize(
        public_key: str, created_at: int, kind: int, tags: List[List[str]], content: str
    ) -> bytes:
        data = [0, public_key, created_at, kind, tags, content]
        data_str: str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return data_str.encode()

    """Generate a sha256 of the event

    Returns:
        str: sha256 hash of the serialised event
    """

    @staticmethod
    def compute_id(
        public_key: str, created_at: int, kind: int, tags: List[List[str]], content: str
    ) -> str:
        return sha256(
            Event.serialize(public_key, created_at, kind, tags, content)
        ).hexdigest()

    """32-bytes lowercase hex-encoded sha256 of the serialized event data

    Returns:
        str: 64-bytes lowercase hex of the signature of the sha256 hash of the serialized event data, which is the same as the "id" field
    """

    @property
    def id(self) -> str:
        # Always recompute the id to reflect the up-to-date state of the Event
        return Event.compute_id(
            self.public_key, self.created_at, self.kind, self.tags, self.content
        )

    @property
    def note_id(self) -> str:
        pass

    @property
    def pub_key(self) -> str:
        return self.public_key

    # def add_pubkey_ref(self, pubkey:str):
    #     """ Adds a reference to a pubkey as a 'p' tag """
    #     self.tags.append(['p', pubkey])

    # def add_event_ref(self, event_id:str):
    #     """ Adds a reference to an event_id as an 'e' tag """
    #     self.tags.append(['e', event_id])

    def verify(self) -> bool:
        pass

    """_summary_
    """

    def to_message(self) -> str:
        return json.dumps(
            [
                ClientMessageType.EVENT,
                {
                    'id': self.id,
                    'pubkey': self.public_key,
                    'created_at': self.created_at,
                    'kind': self.kind,
                    'tags': self.tags,
                    'content': self.content,
                    'sig': self.signature,
                },
            ]
        )

    def to_bytes(self) -> bytes:
        filtered_dict = {k: v for k, v in self.__dict__.items() if k != 'signature'}
        return Event.serialize(*filtered_dict.values())
