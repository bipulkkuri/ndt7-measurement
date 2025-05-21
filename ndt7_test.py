import os
import asyncio
import configparser
import socket

config = configparser.ConfigParser()
config.read('config.ini')

from ndt7_discover import discoverServerURLs
from ndt7_download import download_test
from ndt7_upload import upload_test

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

if __name__ == "__main__":
    file_path =  config.get('mlab', 'ndt_server_config')
    if os.path.exists(file_path):
        print(f"{file_path} already exists. Skipping API call.")
        with open(file_path, "r") as f:
            serverconfig = json.load(f)
    else:
        #serverconfig = discoverServerURLs()
        serverconfig = ""
    localserver =  config.get('mlab', 'localserver')    
    print(f"Server: {localserver}")   
    local_ip = get_local_ip()
    print(f"Client: {local_ip}")   
    print("\nStarting NDT7 tests ...\n")
    asyncio.run(download_test(serverconfig))
    asyncio.run(upload_test(serverconfig))
    print("Finshed NDT7 tests\n") 


