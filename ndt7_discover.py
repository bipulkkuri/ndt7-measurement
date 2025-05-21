import configparser
import requests
import json
import os
from typing import Dict, Optional
import functools

# Load config
config = configparser.ConfigParser()
config.read('config.ini')


@functools.cache
def discoverServerURLs() -> Optional[Dict]: 
    # Get URL from config
    url = config.get('mlab', 'discovery_url')

    try:
        response = requests.get(url)
        response.raise_for_status()
        json_data=response.json()
        if "results" in json_data and json_data["results"][0]:
            result = json_data["results"][0] # picking first record
            machine = result.get("machine")
            hostname = result.get("hostname")
            city = result.get("location", {}).get("city")
            country = result.get("location", {}).get("country")
            urls = result.get("urls", {})
            ws_download = urls.get("ws:///ndt/v7/download")
            ws_upload = urls.get("ws:///ndt/v7/upload")
            wss_download = urls.get("wss:///ndt/v7/download")
            wss_upload = urls.get("wss:///ndt/v7/upload")
           
            return {
                "machine": machine,
                "hostname": hostname,
                "location": {
                    "city": city,
                    "country": country
                },
                "urls": {
                    "ws_download": ws_download,
                    "ws_upload": ws_upload,
                    "wss_download": wss_download,
                    "wss_upload": wss_upload
                }
            }
        else:
            print("No results found in the response.")

    except requests.RequestException as e:
        print(f"Error querying M-Lab locate API: {e}")


if __name__ == "__main__":
    file_path =  config.get('mlab', 'ndt_server_config') # "ndt_server_config.json"
    if os.path.exists(file_path):
        print(f"{file_path} already exists. Skipping API call.")
        with open(file_path, "r") as f:
            result = json.load(f)
    else:
        result = discoverServerURLs()
        print(result)
        if result:
            with open(file_path, "w") as f:
                json.dump(result, f, indent=4)
            print(f"Output saved to {file_path}")
        else:
            print("No data to save.")