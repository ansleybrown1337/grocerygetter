# code to test my api credentials and see if I can access the Kroger API.

import requests
import base64
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("KROGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("KROGER_CLIENT_SECRET")

# Step 1: Base64 encode the client ID and client secret
def get_encoded_credentials(client_id, client_secret):
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    return encoded_credentials

# Step 2: Make a POST request to get an access token
def get_access_token():
    token_url = "https://api.kroger.com/v1/connect/oauth2/token"
    encoded_credentials = get_encoded_credentials(CLIENT_ID, CLIENT_SECRET)
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }
    
    data = {
        "grant_type": "client_credentials"
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        token_response = response.json()
        access_token = token_response.get("access_token")
        print(f"Access Token: {access_token}")
        return access_token
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Step 3: Call the function to test your credentials
if __name__ == "__main__":
    get_access_token()
