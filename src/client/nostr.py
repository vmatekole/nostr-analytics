import asyncio
from email import message

import websockets
from bitcoinlib.keys import Key
from websockets.sync.client import connect

# from bitcoinlib.wallets import


def create_key():
    from pynostr.key import PrivateKey

    private_key = PrivateKey()
    public_key = private_key.public_key
    print(f'Private key: {private_key.bech32}')
    print(f'Public key: {public_key.bech32()}')

    #  private_key, public_key = pysodium.crypto_sign_keypair()
    #  print(private_key.hex())
    #  print(public_key.hex())
    # k = Key()
    # print(f'Secret: {k.private_hex}')
    # print(f'Public: {k.public_hex[2:]}')


async def get_events(websocket, path):
    socket: ClientConnection = connect_relay()
    while True:
        message = await socket.recv()
        print(message)


def connect_relay():
    return websockets.serve(get_events, 'wss://relay.nostr.net', 8080)
