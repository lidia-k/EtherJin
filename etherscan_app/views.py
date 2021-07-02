from django.shortcuts import render
from django.http import HttpResponse
from etherscan_app.utils import validate_address, create_address, create_transaction
from etherscan_app.models import Address, Transaction
from django_q.tasks import async_task

def index(request):
    return render(request, 'etherscan_app/index.html')

def search(request):
    return render(request, 'etherscan_app/search.html')

def show_results(request):
    address = request.POST.get("address")
    valid_address, response_data = validate_address(address)
    result_data = response_data['result']
    
    if valid_address:
        address_instance = create_address(address) 
        async_task('etherscan_app.utils.create_transaction', address_instance, result_data)
        return HttpResponse(f'message: {response_data["message"]}, result: {result_data}')
    elif result_data == 'Invalid API Key':
        print("Please provide a valid api_token.")
        return HttpResponse(status=500)