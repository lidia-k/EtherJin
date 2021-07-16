from django.urls import path

from etherscan_app import views

app_name = 'etherscan_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('results', views.show_results, name='results'),
    path('user_addresses', views.show_user_addresses, name='user_addresses'),
    path('create_list', views.create_list, name='create_list'),
]