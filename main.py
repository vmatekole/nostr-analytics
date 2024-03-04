import ast
import asyncio
import base64
import hashlib
import json
import os
import time

import pysodium
import websockets
from btclib.ecc.libsecp256k1 import ecssa_sign_
from dotenv import load_dotenv

from src.client.nostr import create_key

load_dotenv()


async def listen_to_events():
    uri = 'wss://nostr.lnproxy.org'  # Replace with your Nostr relay address and port
    async with websockets.connect(uri) as websocket:
        while True:
            event = await websocket.recv()
            print(f'Received event: {event}')
            event = json.loads(event)

            if event[0] == 'AUTH':
                m = hashlib.sha256()
                r = hashlib.sha256()
                challenge: str = event[1]

                eventData = {
                    'pubkey': os.getenv('PUB_KEY'),
                    'created_at': int(time.time()),
                    'kind': 22242,
                    'tags': [
                        ['relay', 'wss://nostr.lnproxy.org'],
                        ['challenge', challenge],
                    ],
                }
                req = eventData.copy()
                req['kind'] = 4
                del req['tags']
                r.update(json.dumps(req).encode())

                m.update(json.dumps(eventData).encode())
                priv_key = os.getenv('PRIV_KEY')
                eventData['id'] = m.hexdigest()
                # req['id'] = r.hexdigest()
                eventData['sig'] = base64.b64encode(
                    pysodium.crypto_sign_detached(eventData['id'], priv_key)
                ).decode('utf-8')
                # eventData['sig'] =  base64.b64encode(pysodium.crypto_sign_detached(eventData['id'], priv_key)).decode('utf-8')
                print(eventData)
                # event = await websocket.send(json.dumps(['AUTH', eventData]))
                event = await websocket.send(json.dumps(['REQ', 'sub_1', req]))
                print(f'Response: {event}')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(listen_to_events())
    # create_key()
