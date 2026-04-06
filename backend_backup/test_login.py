import requests
import json

url = "https://timetracker-api-m8k7.onrender.com/api/auth/login"
payload = {
    "email": "admin@tickmarks.com",
    "password": "Admin@123"
}
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    print(f"Request URL: {response.url}")
except Exception as e:
    print(f"Exception: {e}")



