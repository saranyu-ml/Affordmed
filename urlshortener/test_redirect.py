import requests

# The short URL we created earlier
short_url = "http://127.0.0.1:8000/N2tv5m"

# First, check the initial redirect
initial_response = requests.get(short_url, allow_redirects=False)

print("\nTesting redirect functionality:")
print("\nInitial Redirect Status Code:", initial_response.status_code)
print("Initial Redirect Location:", initial_response.headers.get('Location'))

# Now follow the redirects to get the final URL
final_response = requests.get(short_url, allow_redirects=True)
print("\nFinal URL:", final_response.url)

# Verify we ended up at the correct location
if final_response.url == "https://www.google.com/search?q=python+programming":
    print("\nRedirect chain is working correctly!")
    print("The short URL successfully redirects to the original URL")
else:
    print("Redirect chain is not working as expected")
