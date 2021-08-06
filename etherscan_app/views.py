from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.paginator import Paginator

from etherscan_app.forms import (AliasCreationForm, FolderCreationFrom,
                                 FolderRenameForm, FolderSelectionForm)
from etherscan_app.models import Address, AddressUserRelationship, Folder
from etherscan_app.utils import get_address_response


@login_required(login_url="/login")
def index(request):
    return render(request, "etherscan_app/index.html")


@login_required(login_url="/login")
def search_results(request):
    """
    Takes in a search query 
    If the search query is an address that hasn't been searched by an user, validate and save the address first.
    If the search query is an already saved address, redirect to show the transactions.
    If the search query is a folder, returns a list of the matching folders.
    """
    if request.method == "POST":
        search_query = request.POST.get("search-query")
        if search_query.startswith('0x'):
            user = request.user
            address = AddressUserRelationship.objects.filter(address=search_query, user=user).first()
            if address:
                return redirect(reverse('etherscan_app:show-transactions', kwargs={'address': address.address.address } ))
            return redirect(reverse('etherscan_app:submit-address', kwargs={'address': search_query}))
            
        folders = Folder.objects.search(search_query)
        if folders: 
            return render(request, "etherscan_app/folder_search_results.html", {"folders": folders})
        return HttpResponse("No search results..", status=500)


@login_required(login_url="/login")
def submit_address(request, address):
    """
    Takes in a new address that hasn't been search by a user
    Validates the address
    If the address is valid, saves the address to a user and redirects it to show the transactions
    """
    valid_address, response_data = get_address_response(address)
    if not valid_address and not response_data:
        # no api token
        print("Please provide api_token.")
        return HttpResponse(status=500)

    result_data = response_data["result"]
    user = request.user

    if valid_address:
        address_instance, _ = Address.objects.get_or_create(address=address)
        AddressUserRelationship.objects.get_or_create(
            user=user, address=address_instance
        )
        return redirect(reverse('etherscan_app:show-transactions', kwargs={'address': address_instance.pk}))
    elif result_data == "Error! Invalid address format":
        return HttpResponse(f"{result_data}", status=400)
    print(
        f'status:{response_data["status"]}, message: {response_data["message"]}, result: {result_data}'
    )
    return HttpResponse(status=400)


@login_required(login_url="/login")
def show_transactions(request, address):
    """
    Show the transactions of an address, its alias and saved folders
    """
    user = request.user
    alias_name = AddressUserRelationship.objects.filter(user=user, address=address).first().alias
    address_instance = Address.objects.get(address=address, users=user)
    transactions = address_instance.transactions.all()
    folders = address_instance.folders.all()

    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "address": address,
        "alias": alias_name,
        "folders": folders,
        "transactions": transactions, 
        "page_obj": page_obj,
    }
    return render(request, "etherscan_app/show_transactions.html", context=context)


@login_required(login_url="/login")
def create_alias(request, address):
    address = Address.objects.get(address=address)
    alias_creation_form = AliasCreationForm(address=address.address)
    context = {
        "address": address.pk,
        "alias_creation_form": alias_creation_form,
    }
    return render(request, "etherscan_app/create_alias.html", context=context)


@login_required(login_url="/login")
def save_address_alias(request):
    alias_name = request.POST.get("alias")
    address = request.POST.get("address")
    address_user_instance = AddressUserRelationship.objects.get(
        user=request.user, address=address
    )
    address_user_instance.alias = alias_name
    address_user_instance.save()

    return redirect(
        reverse("etherscan_app:show-transactions", kwargs={"address": address})
    )


@login_required(login_url="/login")
def edit_alias(request, address):
    address = Address.objects.get(address=address)
    alias_creation_form = AliasCreationForm(address=address.address)
    context = {
        "address": address.pk,
        "alias_creation_form": alias_creation_form,
    }
    return render(request, "etherscan_app/edit_alias.html", context=context)


@login_required(login_url="/login")
def create_or_select_folder(request, address):
    user = request.user
    if AddressUserRelationship.objects.filter(user=user, alias=address).exists():
        address = AddressUserRelationship.objects.get(
            user=user, alias=address
        ).address.pk

    folder_selection_form = FolderSelectionForm(folders=request.user.folders.all(), address=address)
    folder_creation_form = FolderCreationFrom(submit_text="Create and Save", address=address)
    context = {
        "address": address,
        "folder_selection_form": folder_selection_form,
        "folder_creation_form": folder_creation_form,
    }
    return render(
        request, "etherscan_app/create_or_select_folder.html", context=context
    )


@login_required(login_url="/login")
def save_address_to_folder(request):
    user = request.user
    address = request.POST.get("address")
    address = Address.objects.get(users=user, address=address)
    folder_id = request.POST.get("folder")
    folder = Folder.objects.get(user=user, pk=folder_id)
    address.folders.add(folder)
    return redirect(
        reverse("etherscan_app:show-folder", kwargs={"folder_id": folder_id})
    )


@login_required(login_url="/login")
def show_folder(request, folder_id):
    folder = Folder.objects.get(user=request.user, pk=folder_id)
    folder_privacy = "public"
    if folder.public:
        folder_privacy = "private"
    
    addresses = folder.addresses.all()
    address_user_instances = []
    for address in addresses:
        address_user_instance = AddressUserRelationship.objects.get(
            user=request.user, address=address
        )
        address_user_instances.append(address_user_instance)
    
    context = {
        "folder": folder, 
        "privacy": folder_privacy,
        "address_user_instances": address_user_instances}
    return render(request, "etherscan_app/show_folder.html", context=context)



@login_required(login_url="/login")
def create_folder(request):
    if request.method == "GET":
        folder_creation_form = FolderCreationFrom()
        return render(
            request,
            "etherscan_app/create_folder.html",
            {"folder_creation_form": folder_creation_form},
        )
    else:
        user = request.user
        folder_name = request.POST.get("folder")
        public = request.POST.get("public")
        folder = Folder.objects.create(user=user, name=folder_name, public=public)
        address = request.POST.get("address")
        if address:
            address = Address.objects.get(users=user, address=address)
            address.folders.add(folder)
        return redirect(
            reverse("etherscan_app:show-folder", kwargs={"folder_id": folder.pk})
        )


@login_required(login_url="/login")
def show_folders(request):
    user = request.user
    folders = user.folders.all()
    return render(request, "etherscan_app/show_folders.html", {"folders": folders})


@login_required(login_url="/login")
def change_folder_privacy(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    if folder.public:
        folder.public = False
    else: 
        folder.public = True
    folder.save()
    return redirect(reverse('etherscan_app:show-folder', kwargs={"folder_id": folder_id}))


@login_required(login_url="/login")
def edit_folder_name(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    if request.method == "GET":
        form = FolderRenameForm()
        return render(
            request,
            "etherscan_app/edit_folder_name.html",
            {"folder": folder, "form": form},
        )
    else:
        new_name = request.POST.get("folder_name")
        folder.name = new_name
        folder.save()
        return redirect(
            reverse("etherscan_app:show-folder", kwargs={"folder_id": folder_id})
        )


@login_required(login_url="/login")
def delete_folder(request, folder_id):
    folder = Folder.objects.get(user=request.user, pk=folder_id)
    folder.delete()
    return redirect(reverse("etherscan_app:show-folders"))


@login_required(login_url="/login")
def show_searched_addresses(request):
    user = request.user
    address_user_instances = AddressUserRelationship.objects.filter(user=user).all()
    addresses = [obj.address.address for obj in address_user_instances]

    return render(request, "etherscan_app/searched_addresses.html", {"addresses": addresses})