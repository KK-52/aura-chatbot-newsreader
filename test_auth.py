import requests
import time
import subprocess
import sys
import os

BASE_URL = "http://localhost:8080"
USER = "testuser"
PASS = "testpass"

def test_auth_flow():
    print("--- Testing Auth Flow ---")
    
    # 1. Register
    print("1. Registering user...")
    resp = requests.post(f"{BASE_URL}/register", data={"username": USER, "password": PASS})
    if resp.status_code == 200:
        print("   Success: Registered.")
        token = resp.json()["access_token"]
    elif resp.status_code == 400: # Already exists
        print("   User already exists, trying login...")
        resp = requests.post(f"{BASE_URL}/token", data={"username": USER, "password": PASS})
        if resp.status_code != 200:
            print(f"   Login failed: {resp.text}")
            return
        token = resp.json()["access_token"]
    else:
        print(f"   Registration failed: {resp.text}")
        return

    print(f"   Token: {token[:10]}...")

    # 2. Access Protected Endpoint (Get URLs)
    print("2. Accessing Protected Endpoint (/session/urls)...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/session/urls", headers=headers)
    
    if resp.status_code == 200:
        print("   Success: Access granted.")
        print(f"   URLs: {resp.json()}")
    else:
        print(f"   Failed: {resp.status_code} - {resp.text}")

    # 3. Access without Token
    print("3. Accessing without Token...")
    resp = requests.get(f"{BASE_URL}/session/urls")
    if resp.status_code == 401:
        print("   Success: Access denied (401).")
    else:
        print(f"   Failed: Expected 401, got {resp.status_code}")

if __name__ == "__main__":
    # Ensure server is running or start it?
    # For now assuming server is running.
    # Check if we can connect
    try:
        requests.get(BASE_URL)
        test_auth_flow()
    except:
        print("Server not running. Starting server...")
        # Start server in background
        proc = subprocess.Popen([sys.executable, "main.py"], 
                                env={**os.environ, "PORT": "8080"},
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5) # Wait for startup
        try:
            test_auth_flow()
        finally:
            print("Stopping server...")
            proc.terminate()
