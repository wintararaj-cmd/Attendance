import requests
import sys

def test_search():
    url = "http://localhost:8000/api/v1/attendance/logs"
    params = {"search": "tararaj"}
    print(f"Calling {url} with params {params}")
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logs = data.get("logs", [])
            print(f"Got {len(logs)} logs")
            for log in logs:
                print(f" - {log['employee_name']} ({log['emp_code']})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_search()
