# health check for APIs
from logger import *
from utils import load_config, is_response_successful, check_api_health
from alerts import alert_api_down   
def main():
    try:
        info("monitoring APIs...")
        config = load_config()
        if not config:
            error("No configuration loaded. Exiting.")
            return
        for api in config.get("apis", []):
            info(f"Checking health of API: {api['name']}")
            response = check_api_health(api)
            if not is_response_successful(response):
                alert_api_down(api["name"], response)
    except Exception as e:
        error(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
    info("API health check completed.")