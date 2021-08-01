from etherscan_app.models import Address
from etherscan_app.utils import get_address_response, create_or_update_transaction


def update_transactions():
    addresses_list = Address.objects.all()
    for address_obj in addresses_list:
        address = address_obj.pk
        valid_address, response_data = get_address_response(address)
        if not valid_address and not response_data:
            print("Please provide api_token.")
            return
        result_data = response_data['result']
        create_or_update_transaction(address, result_data)
        print(f'{address} is successfully updated.')
