# /config.py

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def load_config():
    config = {
        "client_id": os.getenv('KROGER_CLIENT_ID'),
        "client_secret": os.getenv('KROGER_CLIENT_SECRET'),
        "redirect_uri": os.getenv('KROGER_REDIRECT_URI'),
    }
    return config
