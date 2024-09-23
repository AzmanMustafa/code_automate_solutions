import requests
import json

# Set your API key
API_KEY = 'u+RweVcw1PT3jnXxnx8g'

# Define the PagerDuty API URL and headers
url = 'https://api.pagerduty.com/services'
headers = {
    'Authorization': f'Token token={API_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.pagerduty+json;version=2'
}

# Define pagination parameters
limit = 100  # Maximum allowed by PagerDuty API
offset = 0   # Start with the first page

# Initialize an empty list to store all service IDs
service_ids = []

# Start pagination loop
while True:
    # Make the API request with pagination
    params = {'limit': limit, 'offset': offset}
    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        services_data = response.json()

        # Extract the service IDs and names
        for service in services_data['services']:
            service_id = service['id']
            service_name = service['name']
            service_ids.append(service_id)
            print(f"Service Name: {service_name}, Service ID: {service_id}")
        
        # Check if there are more services to fetch
        if not services_data['more']:
            break  # No more pages, exit the loop
        
        # Increment the offset for the next page
        offset += limit
    else:
        print(f"Failed to fetch services: {response.status_code}")
        print(response.text)
        break

# Print the list of service IDs
print("\nList of Service IDs:")
print(service_ids)
