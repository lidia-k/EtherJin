from django.shortcuts import render
from django.http import HttpResponse
from etherscan_app.utils import validate_address
from etherscan_app.models import Address, Transaction
from django_q.tasks import async_task

def index(request):
    return render(request, 'etherscan_app/index.html')

def search(request):
    return render(request, 'etherscan_app/search.html')

def create_transaction(transactions):
    Transaction.objects.bulk_create(transactions)

def create_address(request):
    address = request.POST.get("address")
    valid_address, response_data = validate_address(address)
    transaction_data = response_data['result']
    
    if valid_address:
        address_instance = Address.objects.create(address=address)
        transactions = []
        for i in range(len(transaction_data)):
            transaction = transaction_data[i]
            transaction_instance = Transaction(address=address_instance, from_account=transaction['from'], to_account=transaction['to'], value_in_ether=int(transaction['value'])/1e18)
            transactions.append(transaction_instance)
        async_task('etherscan_app.views.create_transaction', transactions)
    return HttpResponse(f'message: {response_data["message"]}, result: {response_data["result"]}')