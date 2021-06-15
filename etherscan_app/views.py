from django.shortcuts import render
from django.http import HttpResponse
from etherscan_app.utils import validate_address
from etherscan_app.models import Address, Transaction

def index(request):
    return render(request, 'etherscan_app/index.html')

def search(request):
    return render(request, 'etherscan_app/search.html')

def create_address(request):
    address = request.POST.get("address")
    valid_address, response_data = validate_address(address)
    transaction_data = response_data['result']
    
    if valid_address:
        address_instance = Address.objects.create(address=address)
        for i in range(len(transaction_data)):
            transaction = transaction_data[i]
            transaction_instance = Transaction.objects.create(address=address_instance, from_account=transaction['from'], to_account=transaction['to'], value=transaction['value'])

    return HttpResponse(f'message: {response_data["message"]}, result: {response_data["result"]}')