"""
grocerygetter.py
Created by AJ Brown
ansleybrown1337@gmail.com
20 Oct 2024

Remember to update the environment.yml and requirements.txt files with any new libraries
used in this file. 
For conda, use the following command:
conda env export --no-builds > environment.yml
For pip, use the following command:
pip freeze > requirements.txt
"""

# Import necessary libraries
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path='code/.env')

# Access Kroger API credentials
kroger_api_key = os.getenv('KROGER_API_KEY')
kroger_api_secret = os.getenv('KROGER_API_SECRET')

# Basic function to check if keys are loaded
def check_api_credentials():
    if kroger_api_key and kroger_api_secret:
        print("API keys loaded successfully.")
    else:
        print("Error: Missing API keys.")

if __name__ == "__main__":
    check_api_credentials()
