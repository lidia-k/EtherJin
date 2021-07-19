from django.urls import path

from etherscan_app import views

app_name = 'etherscan_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('submit_address', views.submit_address, name='submit-address'),
    path('results/<str:address>', views.show_results, name='results'),
    path('save-address-to-folder', views.save_address_to_folder, name="save-address-to-folder"),
    path('folders/<str:folder>', views.show_folder, name="show-folder"),
    path('<str:address>/transactions', views.show_transactions, name='show-transactions'),
    path('user_addresses', views.show_user_addresses, name='user_addresses'),
    path('create-folder', views.create_folder, name='create-folder'),
    path('view-folders', views.show_folders, name="show-folders"),
    path('<str:folder>/edit', views.edit_folder_name, name="edit-folder-name"),
    path('<str:folder>/delete', views.delete_folder, name="delete-folder"),
]