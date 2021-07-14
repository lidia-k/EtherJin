from django.db import models
from django.contrib.auth.models import User


class Address(models.Model):
    user = models.ForeignKey(User, related_name='address', on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=50, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
class Transaction(models.Model):
    address = models.ForeignKey(Address, related_name='transactions', on_delete=models.CASCADE)
    hash = models.CharField(max_length=200, unique=True, primary_key=True)
    from_account = models.CharField(max_length=50)
    to_account = models.CharField(max_length=50)
    value_in_ether = models.DecimalField(max_digits=110, decimal_places=100)

