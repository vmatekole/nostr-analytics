import time

import websocket
from dotenv import load_dotenv

from models.nostr.event import EventKind
from models.nostr.filter import Filter, Filters
from models.nostr.message_type import ClientMessageType
from models.nostr.relay_manager import RelayManager
from utils import log

# import rich
# from rich.logging import RichHandler


load_dotenv()


filters = Filters(initlist=[Filter(kinds=[EventKind.TEXT_NOTE])])
subscription_id = 'foo'
request = [ClientMessageType.REQUEST, subscription_id]
request.extend(filters.to_json_array())

relay_manager = RelayManager()
relay_manager.add_relay('wss://nostr-pub.wellorder.net')
relay_manager.add_relay('wss://relay.damus.io')
relay_manager.add_subscription_on_all_relays(id=subscription_id, filters=filters)
# relay_manager.add_subscription_on_relay(
#     url='wss://relay.damus.io', id=subscription_id, filters=filters
# )
# relay_manager.open_connections({'cert_reqs': ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
time.sleep(1.25)  # allow the connections to open

# message = json.dumps(request)
# print(message)
# relay_manager.p(message)
# time.sleep(1) # allow the messages to send


if __name__ == '__main__':
    websocket.enableTrace(
        traceable=True, handler=log(10).StreamHandler(), level='DEBUG'
    )
    while True:
        if relay_manager.message_pool.has_events():
            event_msg = relay_manager.message_pool.get_event()
            # print(f'From: {event_msg.url} sub_id: {event_msg.subscription_id}')
            # print(event_msg.event)
            time.sleep(1.25)  # allow the connections to open

    # relay_manager.close_connections()
