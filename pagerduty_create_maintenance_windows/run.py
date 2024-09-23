import requests
import pandas as pd
import json
from datetime import datetime
import pytz

# Set your API key
API_KEY = 'u+RweVcw1PT3jnXxnx8g'

# Read the Excel file
excel_file = 'maintenance_windows.xlsx'
df = pd.read_excel(excel_file)

# Define the local timezone (replace 'Asia/Kuala_Lumpur' with your actual local timezone)
local_tz = pytz.timezone('Asia/Kuala_Lumpur')

# Define the PagerDuty API URL and headers
url = 'https://api.pagerduty.com/maintenance_windows'
headers = {
    'Authorization': f'Token token={API_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.pagerduty+json;version=2'
}

# Loop through the Excel rows and create maintenance windows
for index, row in df.iterrows():
    service_id = row['Service ID']
    
    # Parse the start and end times from the Excel file
    start_time_local = local_tz.localize(datetime.strptime(str(row['Start Time']), "%Y-%m-%d %H:%M:%S"))
    end_time_local = local_tz.localize(datetime.strptime(str(row['End Time']), "%Y-%m-%d %H:%M:%S"))
    
    # Convert the times to UTC
    start_time_utc = start_time_local.astimezone(pytz.utc).isoformat()
    end_time_utc = end_time_local.astimezone(pytz.utc).isoformat()
    
    description = row['Description']
    
    data = {
        "maintenance_window": {
            "type": "maintenance_window",
            "start_time": start_time_utc,
            "end_time": end_time_utc,
            "description": description,
            "services": [{"id": service_id, "type": "service_reference"}]
        }
    }

    # Make the API request to create the maintenance window
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        print(f"Maintenance window for {service_id} created successfully.")
    else:
        print(f"Failed to create maintenance window for {service_id}: {response.status_code}")
        print(response.text)
