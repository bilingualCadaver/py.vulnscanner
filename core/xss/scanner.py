import random
import string
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urljoin


# Generates a unique random string for injection testing
def generate_random_string(length=40):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to handle XSS scanning logic
def scan(urls):
    for u in urls:
        print(f"Scanning URL: {u}")
        
        response = requests.get(u)
        soup = BeautifulSoup(response.content, "html.parser")
        
        forms = soup.find_all('form')
        for form in forms:
            test_form(u, form)
        
        query_params = parse_query_params(u)
        if query_params:
            test_query_params(u, query_params)


def parse_query_params(url):
    parsed_url = urlparse(url)
    return parse_qs(parsed_url.query)


# Tests query parameters
def query_params(base_url, query_params):
    print("Testing query parameters for XSS...")
    for param in query_params:
        unique_value = generate_random_string()
        query_params[param] = unique_value
        modified_url = f"{base_url}?{urlencode(query_params)}"
        
        try:
            response = requests.get(modified_url)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {modified_url}: {e}")
            continue
        
        # Check if the injected value is reflected in the response
        if unique_value in response.text:
            print(f"Possible XSS vulnerability found in parameter '{param}' at {modified_url}")
        else:
            print(f"No reflection for parameter '{param}'")


# Tests form inputs
def is_vulnerable_input(input_element):
    vulnerable_types = ['text', 'textarea', 'search', 'email', 'url']
    input_type = input_element.get('type', 'text').lower()

    return input_type in vulnerable_types

def form(base_url, form):
    form_method = form.get('method', 'get').lower()
    action = form.get('action')
    form_action_url = urljoin(base_url, action) if action else base_url
    
    inputs = form.find_all('input')
    form_data = {}
    
    for input_element in inputs:
        if is_xss_vulnerable_input(input_element):
            input_name = input_element.get('name')
            if input_name:
                form_data[input_name] = generate_random_string()
    
    if form_method == 'post':
        response = requests.post(form_action_url, data=form_data)
    else:  # Assuming GET by default
        response = requests.get(form_action_url, params=form_data)
    
    # Check if the injected values are reflected in the response
    for key, value in form_data.items():
        if value in response.text:
            print(f"[*] Possible XSS vulnerability found in form input '{key}' at {form_action_url}")
        else:
            print(f"[*] No reflection for form input '{key}'")

