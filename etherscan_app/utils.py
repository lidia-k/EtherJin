import os

import ratelimiter
import requests

from etherscan_app.models import Address, Transaction


@ratelimiter.RateLimiter(max_calls=5, period=1)
def validate_address(address):
    """
    Takes in an address
    Returns:
    bool (whether or not the address is valid)
    dict (response json)
    """
    api_token = os.environ.get("ETHERSCAN_API_TOKEN")
    if not api_token:
        return None, None

    etherscan_api = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={api_token}'
    response = requests.get(etherscan_api)
    response_data = response.json()
    valid_address = response_data["status"] == "1" and response_data["message"] == "OK"
    
    return valid_address, response_data

def create_transaction(pk, result_data):
    """
    Takes in a valid address
    Populates transaction data of the address 
    """
    address_instance = Address.objects.get(pk=pk)
    transactions = []
    #TODO fix the for loop line: for transaction in result_data
    for i in range(len(result_data)):
        transaction = result_data[i]
        hash = transaction['hash']
        if not address_instance.transactions.filter(hash=hash):
            transaction_instance = Transaction(
                address=address_instance,
                hash=hash,
                from_account=transaction['from'],
                to_account=transaction['to'],
                value_in_ether=float(transaction['value'])/1e18
            )
            transactions.append(transaction_instance)
    Transaction.objects.bulk_create(transactions)
