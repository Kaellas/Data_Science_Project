import requests # For Salling HTTP Requests
import os # For fetching enviroment variables
from openai import OpenAI # For ChatGPT Requests
from dotenv import load_dotenv # For keeping data in an enviroment file
import pprint # For data display

# Load API keys from external enviroment file for data security 
load_dotenv('/Users/pawelgach/Documents/Aarhus Uni/Data Science Project/DSP Python/Data_Science_Project/api_keys.env')

# Set OpenAI Key
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
)

# Set assistant roles
assistant_description_recipe = (
    "You are a chatbot helping people select the best products from Salling Group's BilkaToGo"
    "You'll be given an input from a user. Based on that input, give a natural language recipe"
)

assistant_description_ingredients = (
    "You'll be given a natural language recipe. Extract a list of"
    " products from the recipe, with no amounts, just ingredient names,"
    " in a plaintext comma separated output. Include no other text, just the ingredient names. Reply in Danish."
    " If there are no products, let your output be empty. If the input would be inappropriate or illegal"
    " do not return anything"
)

# Define function to obtain GPT response
def process_query(user_query):
    # Define global variables to store GPT response
    global ingredients_text, ingredients_list, chat_recipe, chat_ingredients

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


# Ask for user query manually
# user_query = input()
# Example:
# user_query = "I wanna make mac n cheese with friends"

# Extract prompts from external file
# Open the text file in read mode
with open('/Users/pawelgach/Desktop/Prompts.txt', 'r') as file:
    # Read all lines from the file
    prompts = file.readlines()

# You can optionally strip newline characters from each line
prompts = [prompt.strip() for prompt in prompts]

# lines now contains each line from the file as an element in the list
print(prompts)

# Run over all predefined prompts

for prompt in prompts:

    # Run GPT response function over user input
    # Response is saved in global variables
    process_query(prompt)

    # Iterating over the ingredients from ChatGPT:

    # List to hold the results
    product_suggestions = []

    # Loop through each ingredient in the list
    for ingredient in ingredients_list:
        # Call the fetch_product_suggestions function
        suggestions = fetch_product_suggestions(ingredient, verbose = False)
        
        # Create a dictionary for each ingredient with its suggestions
        ingredient_dict = {
            "name": ingredient,
            "suggestions": suggestions
        }
        
        # Append the dictionary to the list
        product_suggestions.append(ingredient_dict)


    # For printing manually:

    # Print first part of ChatGPT response
    # print(chat_recipe.choices[0].message.content)

    # Pretty print the list of dictionaries
    # pprint.pprint(product_suggestions)


    # For printing to log file:

    # Open the log file in append mode
    with open("/Users/pawelgach/Desktop/Testing.log", 'a') as log_file:
        # Print user query to log file
        log_file.write("User Query:\n")
        log_file.write(prompt + "\n")
        log_file.write("\n")  # Add a newline for separation

        # Print the first part of the ChatGPT response
        log_file.write("ChatGPT Recipe Response:\n")
        log_file.write(chat_recipe.choices[0].message.content + "\n")
        log_file.write("\n")

        # Print the second part of the ChatGPT response
        log_file.write("ChatGPT Ingredient Response:\n")
        log_file.write(chat_ingredients.choices[0].message.content + "\n")
        log_file.write("\n")

        # Pretty print the list of suggestions
        log_file.write("\nProduct Suggestions from BilkaTGo:\n")
        pprint.pprint(product_suggestions, stream=log_file)
        log_file.write("\n")