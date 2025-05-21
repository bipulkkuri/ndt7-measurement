import os
import json
import argparse
import socket
from ndt7_discover import discoverServerURLs

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

def displaysc(server):
    print(f"Server: {server}")   
    print(f"Client: {get_local_ip()}\n")  

def getserverdetails(config):
    parser = argparse.ArgumentParser(description="Run NDT7 speed tests.")
    parser.add_argument('--local', action='store_true', help="Use the local ndt-server")
    args = parser.parse_args()

    file_path =  config.get('mlab', 'ndt_server_config')
    if args.local:
            server = config.get('mlab', 'localserver')
            downloaduri =config.get('mlab', 'download_url')
            uploaduri = config.get('mlab', 'upload_url')
    elif os.path.exists(file_path):
            print(f"{file_path} already exists. Skipping API call.")
            with open(file_path, "r") as f:
                serverconfig = json.load(f)
                server = serverconfig.get('hostname')
                urls=serverconfig.get('urls')
                downloaduri=urls.get('wss_download')
                uploaduri=urls.get('wss_upload') 

    else:
            print("Discovering server from API...")
            serverconfig = discoverServerURLs()
            # Optional: save discovered config
            with open(file_path, "w") as f:
                json.dump(serverconfig, f)
            server = serverconfig.get('hostname')
            urls=serverconfig.get('urls')
            downloaduri=urls.get('wss_download')
            uploaduri=urls.get('wss_upload')
    return server,downloaduri,uploaduri