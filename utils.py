import json
import os

ADMIN_FILE = 'admin.json'

def load_admin_credentials():
    default_admin = {
        "username": "admin",
        "password": "admin123"  # Password disimpan plain text (tidak aman!)
    }
    try:
        with open(ADMIN_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(ADMIN_FILE, 'w') as f:
            json.dump(default_admin, f, indent=4)
        return default_admin

def save_admin_credentials(credentials):
    with open(ADMIN_FILE, 'w') as f:
        json.dump(credentials, f, indent=4)

# Constants
RUANGAN_FILE = 'ruangan.json'
CUSTOMER_FILE = 'customer.json'
HISTORY_FILE = 'riwayat.json'

def load_json(file_name):
    if not os.path.isfile(file_name):
        return []
    with open(file_name, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

def next_id(data_list):
    if not data_list:
        return 1
    return max(item['id'] for item in data_list) + 1