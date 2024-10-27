import requests
import os
import json

def get_cred():
    api_key = os.getenv("CF_APIKEY")
    auth_email = os.getenv("CF_AUTH_EMAIL")
    if not api_key or not auth_email:
        try:
            with open(".cloudflare_cred", "r") as file:
                creds = dict(line.strip().split('=') for line in file)
                api_key = creds.get("key")
                auth_email = creds.get("email")
        except FileNotFoundError:
            raise Exception("Credentials not found. Please set the CF_APIKEY and CF_AUTH_EMAIL environment variables or create a .cloudflare_cred file.")
    return api_key, auth_email

def get_zone_ids(api_key, auth_email):
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = {
        "X-Auth-Email": auth_email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 400:
        error_data = response.json()
        if error_data["errors"][0]["code"] == 6111:
            raise Exception("Invalid format for Authorization header")
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve zone IDs: {response.status_code} {response.text}")
    data = response.json()
    return [zone["id"] for zone in data["result"]]

def main():
    api_key, auth_email = get_cred()
    zone_ids = get_zone_ids(api_key, auth_email)
    print("Zone IDs:", zone_ids)

if __name__ == "__main__":
    main()
