"""
    The basis of the code below was taken from https://github.com/jeffthibault/python-nostr with some modifications.
"""


class ClientMessageType:
    EVENT = 'EVENT'
    REQUEST = 'REQ'
    CLOSE = 'CLOSE'


class RelayMessageType:
    EVENT = 'EVENT'
    NOTICE = 'NOTICE'
    END_OF_STORED_EVENTS = 'EOSE'

    @staticmethod
    def is_valid(type: str) -> bool:
        if (
            type == RelayMessageType.EVENT
            or type == RelayMessageType.NOTICE
            or type == RelayMessageType.END_OF_STORED_EVENTS
        ):
            return True
        return False
