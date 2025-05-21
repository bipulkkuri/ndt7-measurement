import asyncio
import websockets
import json
import os
import configparser
import ssl
import logging
import argparse
from time import time

from ndt7_discover import discoverServerURLs
from utils import getserverdetails,displaysc

#logging.basicConfig(level=logging.DEBUG)

# Load config
config = configparser.ConfigParser()
config.read('config.ini')

def getnow():
   return int(time() * 1000) #milliseconds

total = 0
start =  getnow()
previous = start
subprotocol = config.get('mlab', 'subprotocols')
async def on_open(websocket):
    global total, start, previous
   
    total=0
    start =  getnow()
    previous = start
    print("Download Started",flush=True)
    await websocket.send("Hello from async client!")

async def on_message(websocket):
    global total
    global previous
    async for message in websocket:
        total +=len(message)
       
        t1 = getnow()
        
        every = 250 #ms
        if (t1 - previous > every):
            #ElapsedTime=(t1 - start) / 1000 # seconds
            meanClientMbps=(total / (t1 - start)) * 0.008
            previous = t1
            print(f"\rDownload: {meanClientMbps:.2f} Mb/s", end=' ', flush=True)
            
    

async def on_close(websocket, reason=None):
    print("\nDownload: Complete", flush=True)
    
async def on_error(e):
    print("\nAn error occurred:", str(e))

async def download_test(uri):
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    websocket = None
    try:
        websocket = await websockets.connect(
            uri,
            subprotocols=[subprotocol],
            ssl=ssl_context
        )


        await on_open(websocket)
        await on_message(websocket)

    except Exception as e:
        await on_error(e)
    finally:
        if websocket:
            await on_close(websocket, reason="Finished or error occurred")


if __name__ == "__main__":
    server, downloaduri, uploaduri = getserverdetails(config)   
    displaysc(server)         
    asyncio.run(download_test(downloaduri))
     