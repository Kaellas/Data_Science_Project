import requests # For Salling HTTP Requests
import os # For fetching enviroment variables
from openai import OpenAI # For ChatGPT Requests
from dotenv import load_dotenv # For keeping data in an enviroment file
import pprint # For data display

# Load API keys from external enviroment file for data security 
load_dotenv('/Users/pawelgach/Documents/Aarhus Uni/Data Science Project/DSP Python/Martin_Paper_Demo/api_keys.env')

# Set OpenAI Key
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
)

# Set assistant roles
assistant_description_recipe = (
    "You'll be given an input from a user. Based on that input, give a natural language recipe"
)

assistant_description_ingredients = (
    "You'll be given an natural language recipe. Extract a list of"
    " ingredients from the recipe, with no amounts, just ingredient names,"
    " in a plaintext comma separated output"
)

# Ask for user query
# user_query = input()
user_query = "I wanna make mac n cheese with friends"

# Fetch ChatGPT reponse for the recipe
chat_recipe = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": user_query,
        },
        {
            "role": "system",
            "content": assistant_description_recipe
        }
    ]
)

# Debugging: print recipe
# print(chat_recipe.choices[0].message.content)

# Fetch list of ingredients
chat_ingredients = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": chat_recipe.choices[0].message.content,
        },
        {
            "role": "system",
            "content": assistant_description_ingredients
        }
    ]
)

# Debugging: print ingredient list
# print(chat_ingredients.choices[0].message.content)

# Extract list of ingredients from ChatGPT response

# Step 1: Strip whitespace from the ingredient list part
ingredients_text = chat_ingredients.choices[0].message.content.strip()

# Step 2: Split the ingredients string into a list of ingredients
ingredients_list = ingredients_text.split(', ')

# For debugging: Print the list of ingredients
# print(ingredients_list)

def fetch_product_suggestions(query, verbose = False):
    """
    Fetches product suggestions from Salling API based on a given query.

    Parameters:
    - query (str): The search query for product suggestions.
    - verbose (bool): If True, prints detailed information about each product.

    Returns:
    - list: A list of product details.
    """

    # Initialize the result list
    result = []
    
    # Base URL
    url = 'https://api.sallinggroup.com/v1-beta/product-suggestions/relevant-products'
    
    # Headers with the auth token
    headers = {
        'Authorization': os.getenv('SALLING_API_KEY')
    }
    
    # Query parameters with dynamic query input
    params = {
        'query': query
    }
    
    # Perform the GET request
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Check if the 'suggestions' key is present in the response
        if 'suggestions' in data:
            # Loop through each item in the suggestions list
            for item in data['suggestions']:
                # Append each product as a list to the result list
                product_details = {
                    'prod_id': item.get('prod_id', 'N/A'),
                    'title': item.get('title', 'No title available'),
                    'description': item.get('description', 'No description available'),
                    'img': item.get('img', 'No image available'),
                    'link': item.get('link', 'No link available'),
                    'price': item.get('price', 'No price available')
                }
                result.append(product_details)

                # Set "verbose" to True to see each call individually
                if verbose:
                    print(f"Product ID: {product_details['prod_id']}")
                    print(f"Title: {product_details['title']}")
                    print(f"Description: {product_details['description']}")
                    print(f"Image URL: {product_details['img']}")
                    print(f"Product Link: {product_details['link']}")
                    print(f"Price: {product_details['price']}")
                    print("----------")
        else:
            print("No suggestions found.")
    else:
        print(f"Failed to retrieve data: {response.status_code}")
    
    return result

# Iterating over the ingredients from ChatGPT:

# List to hold the results
product_suggestions = []

# Loop through each ingredient in the list
for ingredient in ingredients_list:
    # Call the fetch_product_suggestions function
    suggestions = fetch_product_suggestions(ingredient, verbose = True)
    
    # Create a dictionary for each ingredient with its suggestions
    ingredient_dict = {
        "name": ingredient,
        "suggestions": suggestions
    }
    
    # Append the dictionary to the list
    product_suggestions.append(ingredient_dict)

# Print first part of ChatGPT response
print(chat_recipe.choices[0].message.content)

# Pretty print the list of dictionaries
pprint.pprint(product_suggestions)
