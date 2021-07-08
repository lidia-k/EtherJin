from django.http import HttpResponse
from django.shortcuts import render

from django_q.tasks import async_task

from etherscan_app.models import Address
from etherscan_app.utils import validate_address


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
        address_instance, _ = Address.objects.get_or_create(address=address)
        pk = address_instance.pk
        async_task('etherscan_app.utils.create_transaction', pk, result_data)
        return HttpResponse(f"The transaction data of '{address}' is successfully saved.", status=200)
    elif result_data == 'Error! Invalid address format':
        return HttpResponse(f"{result_data}", status=400)
    
    print(f'status:{response_data["status"]}, message: {response_data["message"]}, result: {result_data}')
    return HttpResponse(status=400)