from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from django_q.tasks import async_task

from etherscan_app.forms import (AddressSearchForm, FolderCreationFrom,
                                 FolderRenameForm, FolderSelectionForm)
from etherscan_app.models import Address, Folder
from etherscan_app.utils import validate_address


@login_required(login_url='/')
def index(request):
    return render(request, 'etherscan_app/index.html')

@login_required(login_url='/')
def search(request):
    form = AddressSearchForm()
    return render(request, 'etherscan_app/search.html', {'form': form})

@login_required(login_url='/')
def submit_address(request):
    #TODO make it faster to show the results 
    address = request.POST.get('address')
    valid_address, response_data = validate_address(address)
    if not valid_address and not response_data:
        # no api token
        print("Please provide api_token.")
        return HttpResponse(status=500)

    result_data = response_data['result']
    user = request.user

    if valid_address:
        address_instance, _ = Address.objects.get_or_create(address=address)
        address_instance.users.add(user)
        pk = address_instance.pk
        async_task('etherscan_app.utils.create_transaction', pk, result_data)
        return redirect(reverse('etherscan_app:results', kwargs={'address': address}))
    elif result_data == 'Error! Invalid address format':
        return HttpResponse(f"{result_data}", status=400)
    print(f'status:{response_data["status"]}, message: {response_data["message"]}, result: {result_data}')
    return HttpResponse(status=400)

@login_required(login_url='/')
def show_results(request, address):
    address = Address.objects.get(address=address)
    folder_selection_form = FolderSelectionForm(request.user.folders)
    folder_creation_form = FolderCreationFrom()

    context = {
        'address': address.pk, 
        'folder_selection_form': folder_selection_form,
        'folder_creation_form': folder_creation_form,
    }
    return render(request, 'etherscan_app/results.html', context=context)

@login_required(login_url='/')
def save_address_to_folder(request):
    user = request.user
    address = request.POST.get("address")
    address = Address.objects.get(users=user, address=address)
    folder = request.POST.get('folder')
    folder = Folder.objects.get(user=user, folder=folder)
    address.folders.add(folder)
    return redirect(reverse('etherscan_app:show-folder', kwargs={'folder':folder}))

@login_required(login_url='/')
def show_folder(request, folder):
    folder = Folder.objects.get(user=request.user, folder=folder)
    addresses = folder.addresses.all()
    return render(request, 'etherscan_app/show_folder.html', {'folder': folder, 'addresses': addresses})

@login_required(login_url='/')
def show_transactions(request, address):
    address = Address.objects.get(address=address)
    transactions = address.transactions.all()
    return render(request, 'etherscan_app/show_transactions.html', {'address': address, 'transactions': transactions})

@login_required(login_url='/')
def create_folder(request):
    if request.method == "GET":
        folder_creation_form = FolderCreationFrom()
        return render(request, 'etherscan_app/create_folder.html', {'folder_creation_form': folder_creation_form})
    else: 
        user = request.user
        folder_name = request.POST.get("folder")
        folder = Folder.objects.create(user=user, folder_name=folder_name)
        address = request.POST.get("address")
        if address:
            address = Address.objects.get(users=user, address=address)
            address.folders.add(folder)
        return redirect(reverse('etherscan_app:show-folder', kwargs={'folder':folder}))

@login_required(login_url='/')
def show_folders(request):
    user = request.user
    folders = user.folders.all()
    return render(request, 'etherscan_app/show_folders.html', {'folders': folders})

@login_required(login_url='/')
def edit_folder_name(request, folder):
    if request.method == "GET":
        form = FolderRenameForm()
        return render(request, 'etherscan_app/edit_folder_name.html', {'folder': folder, 'form': form})
    else:
        new_name = request.POST.get('folder_name')
        folder = Folder.objects.get(user=request.user, folder_name=folder)
        folder.folder_name = new_name
        folder.save()
        return redirect(reverse('etherscan_app:show-folder', kwargs={'folder':new_name}))

@login_required(login_url='/')
def delete_folder(request, folder):
    folder = Folder.objects.get(user=request.user, folder_name=folder)
    folder.delete()
    return redirect(reverse('etherscan_app:show-folders'))
