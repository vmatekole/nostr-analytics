import json
import ssl
import time

from nostr.event import Event, EventKind
from nostr.filter import Filter, Filters
from nostr.key import PrivateKey
from nostr.message_type import ClientMessageType
from nostr.relay_manager import RelayManager


def generate_key():
    private_key = PrivateKey()
    public_key = private_key.public_key
    print(f'Private key: {private_key.bech32()}')
    print(f'Public key: {public_key.bech32()}')


def connect_relay():
    relay_manager = RelayManager()
    relay_manager.add_relay('wss://relay.nostrss.re')  # type: ignore
    relay_manager.add_relay('wss://relay.blackbyte.nl')
    relay_manager.open_connections(
        {'cert_reqs': ssl.CERT_NONE}
    )  # NOTE: This disables ssl certificate verification
    time.sleep(1.25)  # allow the connections to open
    print(relay_manager.message_pool.has_eose_notices())
    while relay_manager.message_pool.has_notices():
        notice_msg = relay_manager.message_pool.get_notice()
        print(notice_msg.content)
    relay_manager.close_connections()


def get_subscriptions():
    relay_manager = RelayManager()
    relay_manager.add_relay('wss://nostr-pub.wellorder.net')
    relay_manager.add_relay('wss://relay.damus.io')
    relay_manager.open_connections(
        {'cert_reqs': ssl.CERT_NONE}
    )  # NOTE: This disables ssl certificate verification
    time.sleep(5.25)  # allow the connections to open

    print(relay_manager.relays)
    print(relay_manager.relays['wss://nostr-pub.wellorder.net'].to_json_object())


def get_events():
    filters = Filters([Filter(kinds=[EventKind.TEXT_NOTE])])
    subscription_id = ''
    request = [ClientMessageType.REQUEST, subscription_id]
    request.extend(filters.to_json_array())

    relay_manager = RelayManager()
    relay_manager.add_relay('wss://nostr-pub.wellorder.net')
    relay_manager.add_relay('wss://relay.damus.io')
    relay_manager.add_subscription(subscription_id, filters)
    time.sleep(2.25)  # allow the connections to open

    message = json.dumps(request)
    relay_manager.publish_message(message)
    time.sleep(1)  # allow the messages to send

    while relay_manager.message_pool.has_events():
        event_msg = relay_manager.message_pool.get_event()
        print(event_msg.event.content)

    relay_manager.close_connections()
