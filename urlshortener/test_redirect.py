import requests

short_url = "http://127.0.0.1:8000/N2tv5m"

initial_response = requests.get(short_url, allow_redirects=False)

print("\nTesting redirect functionality:")
print("\nInitial Redirect Status Code:", initial_response.status_code)
print("Initial Redirect Location:", initial_response.headers.get('Location'))
final_response = requests.get(short_url, allow_redirects=True)
print("\nFinal URL:", final_response.url)
if final_response.url == "https://www.google.com/search?q=python+programming":
    print("\nRedirect chain is working correctly!")
    print("The short URL successfully redirects to the original URL")
else:
    print("Redirect chain is not working as expected")
