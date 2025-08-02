import requests
import json

# URL of your Django server
url = "http://127.0.0.1:8000/shorturls/"

# Example data to send
payload = {
    "original_url": "https://www.google.com/search?q=python+programming",
    "validity": 30,
    "shortcode": "testlink"
}

# Make the POST request
response = requests.post(url, json=payload)

# Print the response
print("\nResponse Status Code:", response.status_code)
print("\nResponse Content:")
print(json.dumps(response.json(), indent=2))
