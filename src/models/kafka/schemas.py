from dataclasses import dataclass

from dataclasses_avroschema import AvroModel


@dataclass
class EventTopic(AvroModel):
    content: str
    pubkey: str
    created_at: int
    kind: int
    sig: str
    tags: list[list[str]]
