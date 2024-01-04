# Authentik User Migration

This repository contains scripts for migrating users from Nextcloud to Authentik IDM.

## Migration Process

1. **Export users from Nextcloud:** Run the `nextcloud_user_export.sh` script. This script uses the Nextcloud `occ` command to fetch user information and exports it to a JSON file (`nextcloud_user_info.json`).

    ```bash
    ./nextcloud_user_export.sh
    ```

    Make sure to run this script on the server where Nextcloud is installed and that the user running the script has the necessary permissions to execute the `occ` command.

2. **Import users to Authentik:** Run the `authentik_user_import.py` script. This script reads the user data from `nextcloud_user_info.json`, fetches existing groups from Authentik, and imports the users into Authentik.

    ```bash
    python3 authentik_user_import.py
    ```

    Before running the script, make sure to set the Authentik API credentials and endpoints at the top of the script:

    ```python
    authentik_url = ''  # Authentik URL
    authentik_api_key = ''  # Authentik API key
    authentik_username = ''  # Authentik username
    ```

## Dependencies

- `authentik_user_import.py` requires Python 3 and the `requests` library. You can install `requests` using pip:

    ```bash
    pip install requests
    ```

- `nextcloud_user_export.sh` requires `jq` for processing JSON data. You can install `jq` using the package manager for your system (e.g., `apt`, `yum`, `brew`).

## Note

These scripts are intended for use with the Authentik Identity Provider and Nextcloud. Please ensure you have the necessary permissions and access to the Authentik API and Nextcloud `occ` command before running these scripts.