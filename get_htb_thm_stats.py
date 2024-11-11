
import http.client
import sys
import socket
import os
import json

HTB_API_KEY = os.getenv("HTB_API")
JOJOPUPPE_PROFILE_ID = 1121566
DATA_DIR = "./_data"

SERVICES = {
    "htb": {
        "host": "www.hackthebox.com",
        "endpoint": f"/api/v4/profile/{JOJOPUPPE_PROFILE_ID}",
        "headers": {
            'Authorization': HTB_API_KEY,
            'Cookie': '__cf_bm=UuJBeA5atC3ZSc4y8kEekUDJukFdA3thYmRhaF1eQUI-1731332638-1.0.1.1-zmN_ka9UltKKhuObHt_HG2HJKdvZp1v4WlxAMVG.W3s5t.kZ9nzqtnwm687SD5RlJ_zHf9m7tT1MDUcl4roefA'
        },
        "data_file": os.path.join(DATA_DIR, "htb_stats.json"),
        "label": "HTB-Stat",
        "data_key": "profile"
    },
    "thm": {
        "host": "tryhackme.com",
        "endpoint": "/api/v2/public-profile?username=jojopuppe",
        "headers": {
            'Cookie': 'AWSALB=qy0U3lOQkwIYsgZErzusCGavhpjlglRl1NZDgiDZCt9tzyKlhvhH0Cr0Z6qErESDcxTmOuZNusn7vxcstYLqalkufjDh5UokPaBAAHNHSt8UvrjkZrLiOStbqebk; AWSALBCORS=qy0U3lOQkwIYsgZErzusCGavhpjlglRl1NZDgiDZCt9tzyKlhvhH0Cr0Z6qErESDcxTmOuZNusn7vxcstYLqalkufjDh5UokPaBAAHNHSt8UvrjkZrLiOStbqebk; connect.sid=s%3AEyuNkPNS3yRUT6Hhlxr9U47w1k-8PIHa.mMSXsCTH%2FCvsDSovJ7KLO927LFeEpPYN3PyyK7gtlZw'
        },
        "data_file": os.path.join(DATA_DIR, "thm_stats.json"),
        "label": "THM-Stat",
        "data_key": "data"
    }
}

def fetch_api_data(host, endpoint, headers, timeout=10):
    if host == "www.hackthebox.com" and not headers.get('Authorization'):
        print("Please set HTB_API environment variable and try again", file=sys.stderr)
        return None

    try:
        conn = http.client.HTTPSConnection(host, timeout=timeout)
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        raw_data = res.read().decode("utf-8")

        if res.status == 200:
            try:
                return json.loads(raw_data)
            except json.JSONDecodeError as json_err:
                print(f"JSON decoding failed: {json_err}", file=sys.stderr)
                print("Raw response:", raw_data, file=sys.stderr)
        else:
            print(f"Error: Received HTTP {res.status} - {res.reason}", file=sys.stderr)
            print("Response:", raw_data, file=sys.stderr)
    except http.client.HTTPException as http_err:
        print(f"HTTP error occurred: {http_err}", file=sys.stderr)
    except socket.timeout:
        print("Error: The request timed out", file=sys.stderr)
    except socket.error as socket_err:
        print(f"Socket error occurred: {socket_err}", file=sys.stderr)
    except Exception as err:
        print(f"An unexpected error occurred: {err}", file=sys.stderr)
    finally:
        conn.close()

def load_data(file_path):
    try:
        with open(file_path, 'r') as stats_file:
            return json.load(stats_file)
    except FileNotFoundError:
        print(f"Could not find {file_path}", file=sys.stderr)
    except json.JSONDecodeError as json_err:
        print(f"JSON decoding failed for {file_path}: {json_err}", file=sys.stderr)
    except Exception as err:
        print(f"An error occurred while loading {file_path}: {err}", file=sys.stderr)
    return None

def save_data(file_path, data_dict):
    try:
        with open(file_path, 'w') as stats_file:
            json.dump(data_dict, stats_file, indent=4)
    except Exception as err:
        print(f"Could not save data to {file_path}: {err}", file=sys.stderr)

def update_stats(service):
    new_data = fetch_api_data(
        host=service["host"],
        endpoint=service["endpoint"],
        headers=service["headers"]
    )
    if not new_data:
        return

    current_data = load_data(service["data_file"])
    if not current_data:
        current_data = {}

    current_profile = current_data.get(service["data_key"], {})
    new_profile = new_data.get(service["data_key"], {})

    updated = False
    for key, value in new_profile.items():
        if key not in current_profile:
            print(f"Key: {key} not found in current stats JSON for {service['label']}. Please check.", file=sys.stderr)
        elif current_profile[key] != value:
            print(f"{service['label']}: {key} updated from {current_profile[key]} -> {value}")
            current_profile[key] = value
            updated = True

    if updated:
        current_data[service["data_key"]] = current_profile
        save_data(service["data_file"], current_data)

def main():
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)

    for service_key in SERVICES:
        service = SERVICES[service_key]
        print(f"Getting {service_key.upper()} stats...\n")
        update_stats(service)
        print()

if __name__ == "__main__":
    main()

