from django.shortcuts import render
from django.http import HttpResponse
from etherscan_app.utils import validate_address, create_address
from django_q.tasks import async_task
from etherscan_app.models import Address

def index(request):
    return render(request, 'etherscan_app/index.html')

def search(request):
    return render(request, 'etherscan_app/search.html')

def show_results(request):
    address = request.POST.get("address")
    valid_address, response_data = validate_address(address)

    if not valid_address and not response_data:
        # no api token
        print("Please provide api_token.")
        return HttpResponse(status=500)

    result_data = response_data['result']

    if valid_address:
        import pdb; pdb.set_trace()
        if not Address.objects.filter(address=address):
            create_address(address) 
        address_instance = Address.objects.get(address=address)
        async_task('etherscan_app.utils.create_transaction', address_instance, result_data)
        return HttpResponse(f'message: {response_data["message"]}, result: {result_data}')
    elif result_data == 'Error! Invalid address format':
        return HttpResponse(f"{result_data}", status=400)
    
    print(f'status:{response_data["status"]}, message: {response_data["message"]}, result: {result_data}')
    return HttpResponse(status=500)