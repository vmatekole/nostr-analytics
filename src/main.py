import json
import ssl
import time
from xml.dom.expatbuilder import TEXT_NODE

from dotenv import load_dotenv
from rich import print

from models.nostr.event import EventKind
from models.nostr.filter import Filter, Filters
from models.nostr.message_type import ClientMessageType
from models.nostr.relay_manager import RelayManager

load_dotenv()


filters = Filters([Filter(kinds=[EventKind.TEXT_NOTE])])
subscription_id = 'sub_1'
request = [ClientMessageType.REQUEST, subscription_id]
request.extend(filters.to_json_array())

relay_manager = RelayManager()
relay_manager.add_relay('wss://nostr-pub.wellorder.net')
relay_manager.add_relay('wss://relay.damus.io')
relay_manager.add_subscription_on_relay(
    url='wss://nostr-pub.wellorder.net', id=subscription_id, filters=filters
)
relay_manager.add_subscription_on_relay(
    url='wss://relay.damus.io', id=subscription_id, filters=filters
)
# relay_manager.open_connections({'cert_reqs': ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
time.sleep(1.25)  # allow the connections to open

# message = json.dumps(request)
# print(message)
# relay_manager.p(message)
# time.sleep(1) # allow the messages to send


if __name__ == '__main__':
    while True:
        if relay_manager.message_pool.has_events():
            event_msg = relay_manager.message_pool.get_event()
            print(event_msg.event)
            time.sleep(1.25)  # allow the connections to open

    # relay_manager.close_connections()
