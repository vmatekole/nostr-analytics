"""
    The basis of the code below was taken from https://github.com/jeffthibault/python-nostr with some modifications.
"""
from .filter import Filters


class Subscription:
    def __init__(self, id: str, filters: Filters = None) -> None:
        self.id = id
        self.filters = filters

    def to_json_object(self):
        return {'id': self.id, 'filters': self.filters.to_json_array()}
