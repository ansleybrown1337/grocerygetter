# /kroger_api.py

import requests

# Function to search for a product in Kroger's product database
def search_product(product_name):
    url = f"https://api.kroger.com/v1/products?filter.term={product_name}"
    headers = {
        "Authorization": f"Bearer {access_token}"  # You should pass the actual token here
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        product_data = response.json().get('data', [])
        if product_data:
            return product_data[0]['productId']
    print(f"Failed to find product: {product_name}")
    return None

# Function to add a product to the user's Kroger cart
def add_to_cart(product_id, quantity):
    url = f"https://api.kroger.com/v1/cart/add"
    headers = {
        "Authorization": f"Bearer {access_token}",  # You should pass the actual token here
        "Content-Type": "application/json"
    }
    data = {
        "items": [
            {
                "productId": product_id,
                "quantity": quantity
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"Added product {product_id} to the cart")
    else:
        print(f"Failed to add product to the cart: {response.status_code}")
