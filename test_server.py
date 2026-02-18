
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing Live API...")
    
    # Wait for server to be fully ready (just in case)
    time.sleep(2)
    
    # 1. Ingest
    url_to_ingest = "https://example.com"
    print(f"  Ingesting {url_to_ingest}...")
    try:
        response = requests.post(f"{BASE_URL}/ingest", json={"url": url_to_ingest})
        print(f"  Ingest status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Failed to connect to ingest: {e}")
        return

    # 2. Query
    query = "What is this domain for?"
    print(f"\n  Querying: '{query}'...")
    try:
        response = requests.post(f"{BASE_URL}/query", json={"query": query})
        print(f"  Query status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Answer: {data.get('answer')}")
            if data.get('answer'):
                print("  API Test: PASS")
            else:
                print("  API Test: FAIL (Empty answer)")
        else:
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"  Failed to connect to query: {e}")

if __name__ == "__main__":
    test_api()
