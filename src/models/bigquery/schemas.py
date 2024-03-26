import time
from abc import ABC
from typing import List

from google.cloud import bigquery
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from models.base import BaseBQModel
from models.nostr.event import EventKind


def to_underscore(field_name: str):
    return f'_{field_name}'


class EventRecord(ABC, BaseBQModel):
    model_config = ConfigDict(alias_generator=to_camel)

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
