#!/bin/bash

# Run nextcloud occ command to get user list
user_list=$(sudo -u www-data php /var/www/nextcloud/occ user:list --output=json)

# Print the user list content for verification
echo "$user_list"

# Create an empty array to store user details
user_details=()

# Extract usernames and nicknames using jq
usernames=$(echo "$user_list" | jq -r 'to_entries[] | "\(.key):\(.value)"')

# Fetch user information for each username
while IFS= read -r entry; do
    username=$(echo "$entry" | cut -d ':' -f1)
    
    if [ -n "$username" ]; then
        echo "Fetching info for user: $username"
        # Get user information using user:info for each user
        info=$(sudo -u www-data php /var/www/nextcloud/occ user:info "$username" --output=json)
        
        # Check if the info is not empty and doesn't contain an error message
        if [ -n "$info" ] && ! echo "$info" | grep -q "user not found"; then
            user_details+=("$info")
        else
            echo "Error fetching info for user: $username"
        fi
    fi
done <<< "$usernames"

# Convert the user details array to JSON format
user_details_json=$(printf '%s\n' "${user_details[@]}" | jq -s '.')

# Save the retrieved user details directly to a file
echo "$user_details_json" > nextcloud_user_info.json

echo "User details exported to nextcloud_user_info.json"


