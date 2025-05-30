# health check for APIs
from logger import *
from utils import load_config, is_response_successful, check_api_health, save_to_csv
from alerts import alert_api_down   
def main():
    final_data = []
    try:
        info("monitoring APIs...")
        config = load_config()
        if not config:
            error("No configuration loaded. Exiting.")
            return
        for api in config.get("apis", []):
            info(f"Checking health of API: {api['name']}")
            response = check_api_health(api)

            final_data.append({"API Name": api["name"], "Status Code": response.status_code, "Response Text": response.text})

            if not is_response_successful(response):
                alert_api_down(api["name"], response)
        return final_data
    except Exception as e:
        error(f"Error occurred: {e}")


if __name__ == "__main__":
    data = main()
    print("hehehehe",data)
    if data:
        save_to_csv(data)
    else:
        error("No data to save.")
    info("API health check completed.")