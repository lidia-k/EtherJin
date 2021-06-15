from django.db import models

class Address(models.Model):
    address = models.CharField(max_length=50)

class Transaction(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    from_account = models.CharField(max_length=50)
    to_account = models.CharField(max_length=50)
    value = models.BigIntegerField()
