import asyncio
import websockets
import json
import os
import configparser
import ssl
import logging

from time import time

from ndt7_discover import discoverServerURLs

#logging.basicConfig(level=logging.DEBUG)

# wss://localhost:4443/ndt/v7/download?client_name=ndt-server-example&client_library_name=ndt7-js&client_library_version=0.0.6
# wss://localhost:4443/ndt/v7/upload?client_name=ndt-server-example&client_library_name=ndt7-js&client_library_version=0.0.6
# wss://ndt-mlab2-lga04.mlab-oti.measurement-lab.org/ndt/v7/download?access_token=eyJhbGciOiJFZERTQSIsImtpZCI6ImxvY2F0ZV8yMDIwMDQwOSJ9.eyJhdWQiOlsibWxhYjItbGdhMDQubWxhYi1vdGkubWVhc3VyZW1lbnQtbGFiLm9yZyJdLCJleHAiOjE3NDc4MzMwMDMsImlzcyI6ImxvY2F0ZSIsImp0aSI6ImMyMTI4NzViLWYyZTMtNDc4MS1hY2Y3LTYxM2ZkMzY4YjAxNSIsInN1YiI6Im5kdCJ9.PsPszb81OWFpUPqn5_JHJ0_mVQuQ3_XkiSiaPZHlYjpOXT8xczVwE5WsmG8DgQN1kPknrKDVCmAb4Ud8aeRHBA&client_name=ist&early_exit=250&index=0&locate_version=v2&metro_rank=0
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
    #print("\nDownload Started")
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
            print(f"\rDownload: {meanClientMbps:.2f} Mb/s",end='', flush=True)
            
    

async def on_close(websocket, reason=None):
    print("\n")   
    
async def on_error(e):
    print("\nAn error occurred:", str(e))

async def download_test(serverconfig):
   
    #urls=serverconfig.get('urls')
    #uri=urls.get('wss_download')
    uri =config.get('mlab', 'download_url')
    
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
    file_path =  config.get('mlab', 'ndt_server_config')
    if os.path.exists(file_path):
        print(f"{file_path} already exists. Skipping API call.")
        with open(file_path, "r") as f:
            serverconfig = json.load(f)
    else:
        serverconfig = discoverServerURLs()
        #serverconfig = ""
    asyncio.run(download_test(serverconfig))
     