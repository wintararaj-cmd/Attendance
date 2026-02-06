import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_full_flow():
    print("Testing Full Flow...")
    
    # 1. Login
    print("\n[1] Logging in...")
    login_data = {
        "username": "admin",
        "password": "password123"
    }
    try:
        r = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if r.status_code != 200:
            print(f"Login failed: {r.status_code} - {r.text}")
            return
    except Exception as e:
        print(f"Login connection failed: {e}")
        return
        
    token_data = r.json()
    access_token = token_data.get("access_token")
    if not access_token:
        print("No access token in response")
        return
    print(f"Login successful! Token: {access_token[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # 2. Search Logs (Verified previously, but testing with auth header now)
    print("\n[2] Searching Logs (with Auth)...")
    params = {"search": "tararaj"}
    r = requests.get(f"{BASE_URL}/attendance/logs", params=params, headers=headers)
    print(f"Search Status: {r.status_code}")
    if r.status_code == 200:
        logs = r.json().get("logs", [])
        print(f"Found {len(logs)} logs.")
    else:
        print(f"Search failed: {r.text}")

    # 3. Export Logs
    print("\n[3] Exporting Logs (with Auth)...")
    r = requests.get(f"{BASE_URL}/attendance/export", params=params, headers=headers)
    print(f"Export Status: {r.status_code}")
    if r.status_code == 200:
        lines = r.text.strip().split('\n')
        print(f"Export success! Got {len(lines)} lines.")
    else:
        print(f"Export failed: {r.text}")

if __name__ == "__main__":
    test_full_flow()
