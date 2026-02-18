
import os
from dotenv import load_dotenv
import logging

# Ensure env is loaded
load_dotenv()

# Configure logging to capture output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_groq():
    print("Verifying Groq API Key...")
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("FAIL: GROQ_API_KEY not found in environment.")
        return

    print(f"Key found: {key[:4]}...{key[-4:]}")
    
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=key,
            base_url="https://api.groq.com/openai/v1"
        )
        print("Sending test request to Groq (llama-3.3-70b-versatile)...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Say 'Groq is working!' if you can read this."}
            ]
        )
        content = response.choices[0].message.content
        print(f"Groq Response: {content}")
        
        if "Groq is working" in content:
            print("SUCCESS: Groq API is working correctly.")
        else:
            print("WARNING: unexpected response content.")
            
    except Exception as e:
        print(f"FAIL: Error connecting to Groq: {e}")

if __name__ == "__main__":
    verify_groq()
