# cf-custom-hostname

## Connecting to Cloudflare

To connect to Cloudflare, you need to provide an API key and email. You can do this by either setting environment variables or creating a file with the credentials.

### Using Environment Variables

Set the `CF_APIKEY` and `CF_AUTH_EMAIL` environment variables with your Cloudflare API key and email:

```sh
export CF_APIKEY=your_cloudflare_api_key
export CF_AUTH_EMAIL=your_cloudflare_auth_email
```

### Using a File

Create a file named `.cloudflare_cred` in the same directory as the script and add your Cloudflare API key and email to it in key-value pair format:

```sh
echo "key=your_cloudflare_api_key" > .cloudflare_cred
echo "email=your_cloudflare_auth_email" >> .cloudflare_cred
```

## Setting Up a Virtual Environment

To set up a virtual environment for your Python development, follow these steps:

1. Create a virtual environment:

```sh
python -m venv venv
```

2. Activate the virtual environment:

- On Windows:

```sh
venv\Scripts\activate
```

- On macOS and Linux:

```sh
source venv/bin/activate
```

3. Install the dependencies:

```sh
pip install -r requirements.txt
```

## Running the Script

To run the script, use the following command:

```sh
python main.py
```

The script will print the current zone IDs and domains.

After successful checks, the script will print "All checks successful. Ready to implement custom hostname." and prompt the user with "Do you want to proceed? (yes/no)". If the user confirms with "yes", the script proceeds to the next step. If "no", it exits.

## Running the Unit Test

To run the unit test, use the following command:

```sh
python -m unittest test_main.py
```

## Verifying ACME Challenge

To verify if the relevant ACME challenge name has been configured correctly for a custom hostname, use the following command:

```sh
python main.py --hostname your_custom_hostname
```

The script will use public DNS (8.8.8.8 or 1.1.1.1) to verify the ACME challenge name and CNAME for the provided custom hostname. It will also validate if the CNAME record points to a valid target.

## Error Handling for ACME Challenge Misconfiguration

If the ACME challenge is not properly configured, the script will throw an error. The error message will include the current and desired records for better troubleshooting. Ensure that the ACME challenge and CNAME records are correctly set up in your DNS configuration. Additionally, the script will validate if the CNAME record points to a valid target and include this information in the error message.
