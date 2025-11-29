
import requests
import os
from dotenv import load_dotenv

# Load env directly to be sure
load_dotenv('c:\\khalefa_Whats\\khalefa_Whats\\.env')

BASE_URL = os.getenv('ELMUJIB_API_BASE_URL')
VENDOR_UID = os.getenv('ELMUJIB_VENDOR_UID')
TOKEN = os.getenv('ELMUJIB_BEARER_TOKEN')
PHONE_ID = os.getenv('ELMUJIB_FROM_PHONE_NUMBER_ID')

url = f"{BASE_URL}/{VENDOR_UID}/contact/send-message"
params = {"token": TOKEN}

payload = {
    "phone_number": "201205455559",
    "message_body": "Test Debug Message",
    "from_phone_number_id": PHONE_ID
}

with open('c:\\khalefa_Whats\\khalefa_Whats\\System\\internal_log.txt', 'w') as f:
    f.write(f"Base URL: {BASE_URL}\n")
    f.write(f"Vendor UID: {VENDOR_UID}\n")
    f.write(f"Token: {TOKEN[:10]}...\n")
    f.write(f"Phone ID: {PHONE_ID}\n")
    f.write(f"Sending request to: {url}\n")
    f.write(f"Payload: {payload}\n")

    try:
        response = requests.post(url, params=params, json=payload, timeout=30)
        f.write(f"Status Code: {response.status_code}\n")
        f.write(f"Response Text: {response.text}\n")
        f.write("Request completed.\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
