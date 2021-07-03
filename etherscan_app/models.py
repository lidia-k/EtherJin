from django.db import models

class Address(models.Model):
    address = models.CharField(max_length=50, unique=True)
class Transaction(models.Model):
    address = models.ForeignKey(Address, related_name='transactions', on_delete=models.CASCADE)
    hash = models.CharField(max_length=200, unique=True, default='')
    from_account = models.CharField(max_length=50)
    to_account = models.CharField(max_length=50)
    value_in_ether = models.IntegerField(default=0)
