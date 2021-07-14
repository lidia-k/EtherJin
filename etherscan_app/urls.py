from django.urls import path

from etherscan_app import views

app_name = 'etherscan_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('results', views.show_results, name='results'),
]