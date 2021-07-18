from django.urls import path

from etherscan_app import views

app_name = 'etherscan_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('results/<str:address>', views.show_results, name='results'),
    path('user_addresses', views.show_user_addresses, name='user_addresses'),
    path('create-list', views.create_list, name='create-list'),
    path('submit_address', views.submit_address, name='submit-address'),
    path('view-lists', views.show_folders, name="show-folders"),
    path('save-address-to-folder', views.save_address_to_folder, name="save-address-to-folder"),
]