from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from django_q.tasks import async_task

from etherscan_app.models import Address
from etherscan_app.utils import validate_address


@login_required(login_url='/')
def index(request):
    return render(request, 'etherscan_app/index.html')

@login_required(login_url='/')
def search(request):
    return render(request, 'etherscan_app/search.html')

@login_required(login_url='/')
def show_results(request):
    if request.method == 'POST':
        address = request.POST.get("address")
    else:
        address = request.GET.get('address')
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
        return render(request, 'etherscan_app/results.html', {'address': pk})
    elif result_data == 'Error! Invalid address format':
        return HttpResponse(f"{result_data}", status=400)
    
    print(f'status:{response_data["status"]}, message: {response_data["message"]}, result: {result_data}')
    return HttpResponse(status=400)

@login_required(login_url='/')
def show_user_addresses(request):
    user = request.user
    addresses = user.addresses.all()
    if not addresses: 
        return HttpResponse(f"{user.username}, you aren't following any address yet..", status=404)
    return render(request, 'etherscan_app/user_addresses.html', {'addresses': addresses})