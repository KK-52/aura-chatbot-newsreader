import requests
import sys

def test_ingest():
    url = "http://localhost:8080/ingest"
    payload = {
        "url": "https://www.thenewsminute.com/kerala",
        "session_id": "test-session-123"
    }
    
    print(f"Sending POST request to {url}...")
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200 and response.json().get("status") == "success":
            print("SUCCESS: Live ingestion worked!")
        else:
            print("FAILED: Ingestion did not return success.")
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: Could not connect to server. {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_ingest()
