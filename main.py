import requests
import os
import json

def get_api_key():
    api_key = os.getenv("CF_APIKEY")
    if not api_key:
        try:
            with open(".cloudflare_key", "r") as file:
                api_key = file.read().strip()
        except FileNotFoundError:
            raise Exception("API key not found. Please set the CF_APIKEY environment variable or create a .cloudflare_key file.")
    return api_key

def get_zone_ids(api_key):
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve zone IDs: {response.status_code} {response.text}")
    data = response.json()
    return [zone["id"] for zone in data["result"]]

def main():
    api_key = get_api_key()
    zone_ids = get_zone_ids(api_key)
    print("Zone IDs:", zone_ids)

if __name__ == "__main__":
    main()
