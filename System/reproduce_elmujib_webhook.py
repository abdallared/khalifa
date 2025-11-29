import requests
import json
import os
import sys

# Add the project root to sys.path to access settings if needed, 
# but for this script we just need to hit the URL.

URL = "http://127.0.0.1:8000/api/whatsapp/elmujib/webhook/"
TOKEN = "xY7htGpBoLcB2Y4MVArKYXPe2T8Y5LfOzqnnVK9TwMEhMAewHY9Kibo3uIAd7Ngd"

# Payload mimicking Elmujib
payload = {
    "from": "201205455559",
    "sender_name": "Test User",
    "text": {
        "body": "Test Message from Elmujib Reproduction Script"
    },
    "type": "text",
    "timestamp": 1732700000,
    "id": "wamid.test.12345"
}

# Construct URL with token (query method)
full_url = f"{URL}?token={TOKEN}"

print(f"Sending POST to {full_url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(full_url, json=payload, headers={"Content-Type": "application/json"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
