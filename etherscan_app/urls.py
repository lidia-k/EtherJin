from django.urls import path

from . import views

app_name = 'etherscan_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('results', views.show_results, name='results'),
]