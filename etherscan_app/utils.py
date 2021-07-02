import os
import requests
import json
from ratelimiter import RateLimiter
from etherscan_app.models import Address, Transaction
import sys

@RateLimiter(max_calls=5, period=1)
def validate_address(address):
    """
    Takes in an address
    Returns:
    bool (whether or not the address is valid)
    dict (response json)
    """
    api_token = os.environ.get("API_TOKEN")
    if not api_token:
        return None, None

    etherscan_api = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={api_token}'
    response = requests.get(etherscan_api)
    response_data = json.loads(response.text)
    valid_address = response_data["status"] == "1" and response_data["message"] == "OK"
    
    return (valid_address, response_data)

def create_address(address):  
    """
    Creates an address instance for a valid address 
    """
    address_instance = Address.objects.create(address=address)
    return address_instance

def create_transaction(address_instance, result_data):
    """
    Populate transaction data of a valid address 
    """
    transactions = []
    for i in range(len(result_data)):
        transaction = result_data[i]
        transaction_instance = Transaction(address=address_instance, from_account=transaction['from'], to_account=transaction['to'], value_in_ether=int(transaction['value'])/1e18)
        transactions.append(transaction_instance)
    Transaction.objects.bulk_create(transactions)
