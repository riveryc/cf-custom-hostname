import requests
import os
import json
import dns.resolver

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

def verify_acme_challenge(hostname):
    result = True
    current_record = None
    desired_record = f'_acme-challenge.{hostname}'
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '1.1.1.1']
        answers = resolver.resolve(desired_record, 'TXT')
        for rdata in answers:
            current_record = rdata.to_text()
            print(f'ACME challenge for {hostname}: {current_record}')
    except dns.resolver.NoAnswer:
        print(f'No ACME challenge found for {hostname}. Current record: {current_record}, Desired record: {desired_record}')
        result = False
    except dns.resolver.NXDOMAIN:
        print(f'Hostname {hostname} does not exist. Current record: {current_record}, Desired record: {desired_record}')
        result = False
    except Exception as e:
        print(f'Error verifying ACME challenge for {hostname}: {e}. Current record: {current_record}, Desired record: {desired_record}')
        result = False

    try:
        answers = resolver.resolve(desired_record, 'CNAME')
        for rdata in answers:
            current_record = rdata.to_text()
            print(f'CNAME for {desired_record}: {current_record}')
    except dns.resolver.NoAnswer:
        print(f'No CNAME found for {desired_record}. Current record: {current_record}, Desired record: {desired_record}')
        result = False
    except dns.resolver.NXDOMAIN:
        print(f'Hostname {desired_record} does not exist. Current record: {current_record}, Desired record: {desired_record}')
        result = False
    except Exception as e:
        print(f'Error verifying CNAME for {desired_record}: {e}. Current record: {current_record}, Desired record: {desired_record}')
        result = False

    return result

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Cloudflare custom hostname verification')
    parser.add_argument('--hostname', type=str, help='Custom hostname to verify ACME challenge')
    args = parser.parse_args()

    api_key, auth_email = get_cred()
    zone_ids = get_zone_ids(api_key, auth_email)
    print("Zone IDs:", zone_ids)

    if args.hostname:
        verify_acme_challenge(args.hostname)

if __name__ == "__main__":
    main()
