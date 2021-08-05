from django.urls import path

from etherscan_app import views

app_name = "etherscan_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("search-results", views.search_results, name="search-results"),
    path("submit-address/<str:address>", views.submit_address, name="submit-address"),
    path("create-alias/<str:address>", views.create_alias, name="create-alias"),
    path("edit-alias/<str:address>", views.edit_alias, name="edit-alias"),
    path(
        "save-address-to-folder",
        views.save_address_to_folder,
        name="save-address-to-folder",
    ),
    path("save-alias", views.save_address_alias, name="save-alias"),
    path(
        "create-or-select-folder/<str:address>",
        views.create_or_select_folder,
        name="create-or-select-folder",
    ),
    path("folder/<str:folder_id>", views.show_folder, name="show-folder"),
    path(
        "transactions/<str:address>", views.show_transactions, name="show-transactions"
    ),
    path("create-folder", views.create_folder, name="create-folder"),
    path("view-folders", views.show_folders, name="show-folders"),
    path("<str:folder_id>/edit", views.edit_folder_name, name="edit-folder-name"),
    path("<str:folder_id>/delete", views.delete_folder, name="delete-folder"),
    path("searched-addresses", views.show_searched_addresses, name="searched-addresses"),
]
