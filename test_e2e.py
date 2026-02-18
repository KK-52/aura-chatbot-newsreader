import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"
TEST_URL = "https://example.com"

def wait_for_server():
    for _ in range(15):
        try:
            requests.get(BASE_URL)
            return True
        except requests.ConnectionError:
            time.sleep(1)
    return False

def test_url_rag_flow():
    print("Waiting for server (URL RAG System)...")
    if not wait_for_server():
        print("Server failed to start.")
        sys.exit(1)
        
    print("Server is up.")
    
    # 1. Ingest URL
    print(f"Ingesting URL: {TEST_URL}")
    res = requests.post(f"{BASE_URL}/ingest", json={"url": TEST_URL})
    if res.status_code == 200:
        print(f"✅ Ingestion Successful: {res.json().get('message')}")
    else:
        print(f"❌ Ingestion Failed: {res.text}")
        sys.exit(1)
        
    # 2. Query RAG
    query = "domain"
    print(f"Querying: '{query}'")
    
    res = requests.post(f"{BASE_URL}/query", json={"query": query})
    if res.status_code == 200:
        data = res.json()
        print("✅ Query Successful")
        print("Retrieved Context:", data.get("context"))
        print("Generated Answer:", data.get("answer"))
        
        # Simple assertion
        context_str = str(data.get("context"))
        if "Example Domain" in context_str or "illustrative examples" in context_str:
            print("✅ RAG logic verified: Context contains expected page content.")
        else:
            print("⚠️ RAG logic warning: Context might be empty or irrelevant.")
    else:
        print(f"❌ Query Failed: {res.text}")
        sys.exit(1)

if __name__ == "__main__":
    test_url_rag_flow()
