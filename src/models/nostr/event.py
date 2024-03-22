"""
    The basis of the code below was taken from https://github.com/jeffthibault/python-nostr with some modifications.
"""
import json
import time
from ast import alias
from enum import IntEnum
from hashlib import sha256
from typing import Any, List

from pydantic import BaseModel, Field, model_serializer
from pydantic.dataclasses import dataclass
from typing_extensions import Annotated

from .message_type import ClientMessageType


class EventKind(IntEnum):
    SET_METADATA = 0
    TEXT_NOTE = 1
    RECOMMEND_RELAY = 2
    CONTACTS = 3
    ENCRYPTED_DIRECT_MESSAGE = 4
    DELETE = 5


@dataclass
class Event(BaseModel):
    content: str = Field(description='"text": "nostr txt content"')
    pubkey: str = Field(
        description='"public key": "32-bytes lowercase hex-encoded public key of the event creator"'
    )
    created_at: int = Field(
        default=int(time.time()), description='"seconds": "unix timestamp in seconds"'
    )
    kind: int = EventKind.TEXT_NOTE
    sig: str = Field(
        default=None,
        description='"event signature": "64-bytes lowercase hex of the signature of the sha256 hash of the serialized event data, which is the same as the \"id\" field"',
    )
    tags: List[List[str]] = Field(
        default_factory=list, description='"content tag": "arbitrary string"'
    )

    # """Initialises 'content' and 'created_at' fields post initialisation
    # """

    # def __post_init__(self) -> None:
    #     if self.content is not None and not isinstance(self.content, str):
    #         # DMs initialize content to None but all other kinds should pass in a str
    #         raise TypeError("Argument 'content' must be of type str")

    """Serialises Event obj to a byte string

    Returns:
        bytes: Serialized Event obj
    """

    @model_serializer
    def serialize(self) -> bytes:
        data = [0, self.pubkey, self.created_at, self.kind, self.tags, self.content]
        data_str: str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return data_str.encode()

    @staticmethod
    def parse_event(e) -> 'Event':
        e.pop(
            'id'
        )  # The id is always computed, check compute_id function for reference
        return Event(**e)

    """Generate a sha256 of the event

    Returns:
        str: sha256 hash of the serialised event
    """

    def compute_id(self) -> str:
        return sha256(self.serialize(self)).hexdigest()

    """32-bytes lowercase hex-encoded sha256 of the serialized event data

    Returns:
        str: 64-bytes lowercase hex of the signature of the sha256 hash of the serialized event data, which is the same as the "id" field
    """

    @property
    def id(self) -> str:
        # Always recompute the id to reflect the up-to-date state of the Event
        return self.compute_id()

    @property
    def note_id(self) -> str:
        pass

    @property
    def pub_key(self) -> str:
        return self.pubkey

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
                    'pubkey': self.pubkey,
                    'created_at': self.created_at,
                    'kind': self.kind,
                    'tags': self.tags,
                    'content': self.content,
                    'sig': self.sig,
                },
            ]
        )

    def to_bytes(self) -> bytes:
        return self.serialize(self)
