# /auth.py

import requests
from dotenv import load_dotenv
import os
from requests.auth import HTTPBasicAuth

load_dotenv()

CLIENT_ID = os.getenv('KROGER_CLIENT_ID')
CLIENT_SECRET = os.getenv('KROGER_CLIENT_SECRET')
REDIRECT_URI = os.getenv('KROGER_REDIRECT_URI')

# Step 1: Build the authorization URL and get the authorization code
def get_authorization_code():
    auth_url = "https://api.kroger.com/v1/connect/oauth2/authorize"
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "cart.basic:write profile.compact product.compact",
    }
    auth_request_url = requests.Request('GET', auth_url, params=params).prepare().url
    print(f"Visit this URL to authorize the app: {auth_request_url}")
    return input("Enter the authorization code you received: ")

# Step 2: Exchange authorization code for an access token
def get_access_token():
    code = get_authorization_code()
    token_url = "https://api.kroger.com/v1/connect/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    response = requests.post(token_url, auth=auth, data=data)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Failed to retrieve access token")
        return None

# Step 3: Refresh access token if expired
def refresh_access_token(refresh_token):
    token_url = "https://api.kroger.com/v1/connect/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    response = requests.post(token_url, auth=auth, data=data)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Failed to refresh token")
        return None
