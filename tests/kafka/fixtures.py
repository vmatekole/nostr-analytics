import pytest


@pytest.fixture(scope='class')
def kafka_event_topic() -> str:
    return '{"type": "record", "name": "EventTopic", "fields": [{"name": "content", "type": "string"}, {"name": "pubkey", "type": "string"}, {"name": "created_at", "type": "long"}, {"name": "kind", "type": "long"}, {"name": "sig", "type": "string"}, {"name": "tags", "type": {"type": "array", "items": {"type": "array", "items": "string", "name": "tag"}, "name": "tag"}}]}'
