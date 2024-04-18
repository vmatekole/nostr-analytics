"""
    The basis of the code below was taken from https://github.com/jeffthibault/python-nostr with some modifications.
"""
import json
import time
from enum import IntEnum
from hashlib import sha256
from typing import Any, List, Optional

from pydantic import Field
from pydantic.fields import FieldInfo

from nostr.base import ModelBase

from .message_type import ClientMessageType


class EventKind(IntEnum):
    SET_METADATA = 0
    TEXT_NOTE = 1
    LONG_FORM_CONTENT = 30023
    REACTIONS = 7
    RECOMMEND_RELAY = 2
    CONTACTS = 3
    ENCRYPTED_DIRECT_MESSAGE = 4
    DELETE = 5


class Event(ModelBase):
    content: Optional[str] = Field(description='"text": "nostr txt content"')
    pubkey: str = Field(
        description='"public key": "32-bytes lowercase hex-encoded public key of the event creator"'
    )
    created_at: int = Field(
        default=int(time.time()), description='"seconds": "unix timestamp in seconds"'
    )
    kind: int = Field(
        default=EventKind.TEXT_NOTE,
        description='nostr event kinds see https://nostrdata.github.io/kinds/',
    )
    sig: str = Field(
        default=None,
        description='"event signature": "64-bytes lowercase hex of the signature of the sha256 hash of the serialized event data, which is the same as the \"id\" field"',
    )
    tags: Optional[List[List[str]]] = Field(
        default_factory=list, description='"content tag": "arbitrary string"'
    )

    """Serialises Event obj to a json string in byte from
    Returns:
        bytes: Serialized Event obj
    """

    def to_json_bytes_str(self) -> bytes:
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
        return sha256(self.to_json_bytes_str()).hexdigest()

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

    def verify(self) -> bool:
        pass

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

    def to_dict(self) -> dict[str, Any]:
        event: dict[str, Any] = self.model_dump()

        bq_tag_repr = [
            ({'tag_id': index, 'tag_values': tag_array})
            for index, tag_array in enumerate(event['tags'])
        ]
        event['tags'] = bq_tag_repr
        return event

    @staticmethod
    def _get_field_mode(name: str, field: FieldInfo):

        if not name in ['sig', 'content'] and field.default is not None:
            return 'NOT NULL'
        else:
            return 'NULLABLE'
