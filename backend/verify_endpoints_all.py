import urllib.request
import json
import ssl
import traceback

def check_endpoint():
    endpoints = [
        "http://localhost:8000/api/v1/departments",
        "http://localhost:8000/api/v1/employees",
        "http://localhost:8000/api/v1/dashboard/stats"
    ]
    
    for url in endpoints:
        print(f"\nChecking {url}")
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                print(f"Status: {response.status}")
                data = response.read()
                print(f"Data: {data.decode('utf-8')[:50]}...") 

        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            error_content = e.read().decode('utf-8')
            print(f"Error Content: {error_content}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_endpoint()
