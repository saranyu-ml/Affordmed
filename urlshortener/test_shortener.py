import requests
import json
url = "http://127.0.0.1:8000/shorturls/"

payload = {
    "original_url": "https://www.google.com/search?q=python+programming",
    "validity": 30,
    "shortcode": "testlink"
}

response = requests.post(url, json=payload)

print("\nResponse Status Code:", response.status_code)
print("\nResponse Content:")
print(json.dumps(response.json(), indent=2))
