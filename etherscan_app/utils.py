import os
import requests
import json
from ratelimiter import RateLimiter

@RateLimiter(max_calls=5, period=1)
def validate_address(address):
    """
    Takes in an address
    Returns:
    bool (whether or not the address is valid)
    dict (response json)
    """
    api_token = os.environ.get("API_TOKEN")
    etherscan_api = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={api_token}'
    
    response = requests.get(etherscan_api)
    response_data = json.loads(response.text)
    valid_address = response_data["status"] == "1" and response_data["message"] == "OK"
    return (valid_address, response_data)
    