import urllib.request
import json
import ssl

def check_endpoint():
    url = "http://localhost:8000/api/v1/departments"
    print(f"Checking {url}")
    try:
        # Create a request
        req = urllib.request.Request(url)
        # Add headers if needed
        # req.add_header('Authorization', 'Bearer ...') 
        
        with urllib.request.urlopen(req) as response:
            print(f"Status: {response.status}")
            data = response.read()
            print(f"Data: {data.decode('utf-8')[:500]}...") # Print first 500 chars

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        error_content = e.read().decode('utf-8')
        print(f"Error Content: {error_content}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_endpoint()
