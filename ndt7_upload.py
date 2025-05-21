import asyncio
import websockets
import json
import os
import configparser
import ssl
from time import time
import logging

from ndt7_discover import discoverServerURLs

#logging.basicConfig(level=logging.DEBUG)
config = configparser.ConfigParser()
config.read('config.ini')

def getnow():
    return int(time() * 1000)  # milliseconds

max_message_size = 8 * 1024 * 1024  # 8 MB
client_measurement_interval = 0.25  # seconds

async def uploader(websocket, data, start, end):
    total = 0
    previous = start

    while True:
        t = getnow()

        if t >= end:
            await websocket.close()
            break

        # Simulate adaptive buffer sizing (not precise without .buffered_amount)
        if len(data) < max_message_size:
            data = bytearray(min(len(data) * 2, max_message_size))  # Cap at 8MB

        await websocket.send(data)
        total += len(data)

        if t >= previous + client_measurement_interval * 1000:
            elapsed_time = (getnow() - start) / 1000
            mean_mbps = total * 8 / 1_000_000 / elapsed_time
            print(f"\rUpload: {mean_mbps:.2f} Mb/s", end='', flush=True)
            previous = t

        await asyncio.sleep(0.001)  # Yield control to the event loop

async def on_open(websocket):
    #print("\nUpload Started")
    initial_message_size = 8192
    data = bytearray(initial_message_size)
    duration = 10000  # ms
    start = getnow()
    end = start + duration
    await uploader(websocket, data, start, end)

async def on_close(websocket, reason=None):
    #print("\nUpload Completed")
     print("\n")

async def on_error(e):
    print("An error occurred:", str(e))

async def on_message(websocket):
    pass  # Handle incoming messages if necessary

async def upload_test(serverconfig):
    uri = config.get('mlab', 'upload_url')
    #urls=serverconfig.get('urls')
    #uri=urls.get('wss_download')
    subprotocol = config.get('mlab', 'subprotocols')

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    websocket = None
    try:
        websocket = await websockets.connect(
            uri,
            subprotocols=[subprotocol],
            ssl=ssl_context,
            max_size=None
        )
        await on_open(websocket)
        await on_message(websocket)

    except Exception as e:
        await on_error(e)
    finally:
        if websocket:
            await on_close(websocket, reason="Finished or error occurred")

if __name__ == "__main__":
    file_path = config.get('mlab', 'ndt_server_config')
    if os.path.exists(file_path):
        print(f"{file_path} already exists. Skipping API call.")
        with open(file_path, "r") as f:
            serverconfig = json.load(f)
    else:
        #serverconfig = discoverServerURLs()
        serverconfig=""

    asyncio.run(upload_test(serverconfig))
