import json
import requests
from types import SimpleNamespace
from logger import *

def load_config():
    """
    Load the configuration from a JSON file.
    """
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
        info("Configuration loaded successfully.")
        return config
    except FileNotFoundError:
        error("Configuration file not found.")
    except json.JSONDecodeError:
        error("Error decoding JSON from the configuration file.")

def is_response_successful(response):
    """
    Check if the API response is successful.
    """
    if response is None:
        error("Response is None, cannot check status.")
        return False
    if response.status_code != 200 and response.status_code != 201:
        error(f"API responded with an error status code: {response.status_code}. Response text: {response.text}")
        return False
    return True
def check_api_health(api):
    """
    Check the health of a given API.
    This is a placeholder function; implement actual API health check logic.
    """
    try:
        response = requests.get(api["url"], timeout=api.get("timeout", 5))
        info(f"Checked {api['name']} - Status Code: {response.status_code}")
        return response
    except requests.RequestException as e:
        error(f"Error checking {api['name']}: {e}")
        response = SimpleNamespace(status_code=500, text=str(e))
        return response