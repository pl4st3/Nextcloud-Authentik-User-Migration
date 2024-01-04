import json
import requests

# Authentik API credentials and endpoints
authentik_url = ''
authentik_api_key = ''
authentik_username = ''

# Read the contents of nextcloud_user_info.json
print("Reading nextcloud_user_info.json...")
with open('nextcloud_user_info.json', 'r') as file:
    user_info = json.load(file)

# Extract all groups from user records
all_groups = set()
for user_record in user_info:
    all_groups.update(user_record["groups"])

# Create a session
session = requests.Session()

# Define headers
headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + authentik_api_key,
}

# Fetch existing groups from Authentik
print("Fetching existing groups from Authentik...")
authentik_groups_url = f'{authentik_url}/api/v3/core/groups/'  # Updated API endpoint
response = session.get(authentik_groups_url, headers=headers)
print(f"Groups URL ({authentik_groups_url}")

# Check for successful response and decode JSON if present
if response.status_code == 200:
    try:
        authentik_groups = response.json()
        print("Existing groups fetched successfully.")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
        authentik_groups = []
elif response.status_code == 404:
    print("The requested resource could not be found. Please check the URL or the resource.")
else:
    print(f"Failed to fetch existing groups. Status Code: {response.status_code}")
    authentik_groups = []

# Check if groups from Nextcloud exist in Authentik, create missing groups
missing_groups = all_groups - set(authentik_groups)
for group in missing_groups:
    group_data = {"name": group}
    create_group_response = session.post(authentik_groups_url, json=group_data, headers=headers)    
    if create_group_response.status_code == 201:
        print(f"Group '{group}' created successfully.")
    else:
        print(f"Failed to create group '{group}'. Status Code: {create_group_response.status_code}")

# Fetch existing groups from Authentik
print("Fetching existing groups from Authentik...")
response = session.get(authentik_groups_url, headers=headers)
authentik_groups = response.json()
#print(authentik_groups)

# Create a dictionary mapping group names to group UUIDs
group_name_to_uuid = {group['name']: group['pk'] for group in authentik_groups['results']}
print(group_name_to_uuid)

# Import users to Authentik
print(f"Importing users to Authentik ({authentik_url})...")
for idx, user_record in enumerate(user_info, start=1):
    print(f"Processing user {idx}/{len(user_info)} - ID: {user_record['user_id']}")

    # Map Nextcloud groups to Authentik group UUIDs
    authentik_group_uuids = [group_name_to_uuid[group] for group in user_record['groups'] if group in group_name_to_uuid]


    # Format the user record according to Authentik's requirements
    formatted_user = {
        "username": user_record["user_id"],
        "name": user_record["display_name"],
        "email": user_record["email"],
        "groups": authentik_group_uuids,
        "is_active": True,  # Assuming all users are active
        "type": "internal",  # Assuming all users are internal
        # Add other fields as required by Authentik's API
        # Map or transform data fields according to Authentik's expected format
    }
    
    # Send the formatted user data to Authentik's API endpoint for user import
    user_import_url = f"{authentik_url}/api/v3/core/users/"  # Updated API endpoint
    user_import_response = session.post(user_import_url, json=formatted_user, headers=headers  )

    # Check response status or handle errors based on the API response
    if user_import_response.status_code == 201:
        print(f"User {formatted_user['username']} imported successfully.")
    elif user_import_response.status_code == 400 and user_import_response.json().get('username') == ["This field must be unique."]:
        print(f"User {formatted_user['username']} already exists. Skipping.")
    else:
        print(f"Failed to import user {formatted_user['username']}. Status Code: {user_import_response.status_code}")
        # Print response content for debugging (if needed)
        print(user_import_response.content)