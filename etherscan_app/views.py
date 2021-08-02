from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from etherscan_app.forms import (AddressSearchForm, FolderCreationFrom,
                                 FolderRenameForm, FolderSelectionForm, 
                                 AliasCreationForm)
from etherscan_app.models import Address, Folder, AddressUserRelationship
from etherscan_app.utils import get_address_response


@login_required(login_url='/login')
def index(request):
    return render(request, 'etherscan_app/index.html')

@login_required(login_url='/login')
def search(request):
    form = AddressSearchForm()
    return render(request, 'etherscan_app/search.html', {'form': form})

@login_required(login_url='/login')
def submit_address(request):
    #TODO make it faster to show the results 
    address = request.POST.get('address')
    valid_address, response_data = get_address_response(address)
    if not valid_address and not response_data:
        # no api token
        print("Please provide api_token.")
        return HttpResponse(status=500)

    result_data = response_data['result']
    user = request.user

    if valid_address:
        address_instance, _ = Address.objects.get_or_create(address=address)
        AddressUserRelationship.objects.get_or_create(user=user, address=address_instance)
        pk = address_instance.pk
        return redirect(reverse('etherscan_app:results', kwargs={'address': pk}))
    elif result_data == 'Error! Invalid address format':
        return HttpResponse(f"{result_data}", status=400)
    print(f'status:{response_data["status"]}, message: {response_data["message"]}, result: {result_data}')
    return HttpResponse(status=400)

@login_required(login_url='/login')
def show_results(request, address):
    address = Address.objects.get(address=address)
    alias_creation_form = AliasCreationForm(address=address.address)
    context = {
        'address': address.pk, 
        'alias_creation_form': alias_creation_form,
    }
    return render(request, 'etherscan_app/results.html', context=context)

@login_required(login_url='/login')
def save_address_alias(request):
    print(request.POST.get('alias'))
    alias_name = request.POST.get('alias')
    address = request.POST.get('address')
    address_user_instance = AddressUserRelationship.objects.get(user=request.user, address=address)
    address_user_instance.alias = alias_name
    address_user_instance.save()

    address = alias_name
    return redirect(reverse('etherscan_app:create-or-select-folder', kwargs={'address': address}))

@login_required(login_url='/login')
def create_or_select_folder(request, address):
    user = request.user
    if  AddressUserRelationship.objects.filter(user=user, alias=address).exists():
        address = AddressUserRelationship.objects.get(user=user, alias=address).address.pk

    folder_selection_form = FolderSelectionForm(request.user.folders.all())
    folder_creation_form = FolderCreationFrom(submit_text='Create and Save')
    context = {
        'address': address, 
        'folder_selection_form': folder_selection_form,
        'folder_creation_form': folder_creation_form,
    }
    return render(request, 'etherscan_app/create_or_select_folder.html', context=context)

@login_required(login_url='/login')
def save_address_to_folder(request):
    user = request.user
    address = request.POST.get("address")
    address = Address.objects.get(users=user, address=address)
    folder_id = request.POST.get('folder')
    folder = Folder.objects.get(user=user, pk=folder_id)
    address.folders.add(folder)
    return redirect(reverse('etherscan_app:show-folder', kwargs={'folder_id':folder_id}))

@login_required(login_url='/login')
def show_folder(request, folder_id):
    folder = Folder.objects.get(user=request.user, pk=folder_id)
    addresses = folder.addresses.all()

    address_user_instances = []
    for address in addresses:
        address_user_instance = AddressUserRelationship.objects.get(user=request.user, address=address)
        address_user_instances.append(address_user_instance)
            
    return render(request, 'etherscan_app/show_folder.html', {'folder': folder, 'address_user_instances': address_user_instances})

@login_required(login_url='/login')
def show_transactions(request, address):
    user = request.user
    if AddressUserRelationship.objects.filter(user=user, alias=address).exists():
        address_instance = AddressUserRelationship.objects.get(user=request.user, alias=address).address
    else: 
        address_instance = Address.objects.get(users=user, pk=address)
    transactions = address_instance.transactions.all()
    return render(request, 'etherscan_app/show_transactions.html', {'address': address, 'transactions': transactions})

@login_required(login_url='/login')
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
        return redirect(reverse('etherscan_app:show-folder', kwargs={'folder_id':folder.pk}))

@login_required(login_url='/login')
def show_folders(request):
    user = request.user
    folders = user.folders.all()
    return render(request, 'etherscan_app/show_folders.html', {'folders': folders})

@login_required(login_url='/login')
def edit_folder_name(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    if request.method == "GET":
        form = FolderRenameForm()
        return render(request, 'etherscan_app/edit_folder_name.html', {'folder': folder, 'form': form})
    else:
        new_name = request.POST.get('folder_name')
        folder.folder_name = new_name
        folder.save()
        return redirect(reverse('etherscan_app:show-folder', kwargs={'folder_id':folder_id}))

@login_required(login_url='/login')
def delete_folder(request, folder_id):
    folder = Folder.objects.get(user=request.user, pk=folder_id)
    folder.delete()
    return redirect(reverse('etherscan_app:show-folders'))
