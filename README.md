# cf-custom-hostname

## Connecting to Cloudflare

To connect to Cloudflare, you need to provide an API key. You can do this by either setting an environment variable or creating a file with the API key.

### Using Environment Variable

Set the `CF_APIKEY` environment variable with your Cloudflare API key:

```sh
export CF_APIKEY=your_cloudflare_api_key
```

### Using a File

Create a file named `.cloudflare_key` in the same directory as the script and add your Cloudflare API key to it:

```sh
echo "your_cloudflare_api_key" > .cloudflare_key
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

The script will print the current zone IDs.

## Running the Unit Test

To run the unit test, use the following command:

```sh
python -m unittest test_main.py
```
