from django.contrib.auth.models import User
from django.db import models

from elasticsearch_dsl import Q as ESQ

from etherscan_app.indexes import FolderDocument


class FolderQuerySet(models.QuerySet):
    def search(self, search_query):
        query = ESQ(
            "multi_match",
            query=search_query,
            type="cross_fields",
            fields=["folder_name"],
        )

        res = FolderDocument.search().query(query).execute()
        folder_ids = [hit.id for hit in res.hits]
        folders = self.filter(id__in=folder_ids)


class Folder(models.Model):
    user = models.ForeignKey(User, related_name="folders", on_delete=models.CASCADE)
    folder_name = models.CharField(max_length=50)

    objects = FolderQuerySet.as_manager()

    def __str__(self):
        return self.folder_name


class AddressUserRelationship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey("Address", on_delete=models.CASCADE)
    alias = models.CharField(max_length=20, null=True, default=None, unique=True)


class Address(models.Model):
    users = models.ManyToManyField(
        User, related_name="addresses", through=AddressUserRelationship
    )
    folders = models.ManyToManyField(Folder, related_name="addresses")
    address = models.CharField(max_length=50, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    address = models.ForeignKey(
        Address, related_name="transactions", on_delete=models.CASCADE
    )
    hash = models.CharField(max_length=200, unique=True, primary_key=True)
    from_account = models.CharField(max_length=50)
    to_account = models.CharField(max_length=50)
    value_in_ether = models.DecimalField(max_digits=110, decimal_places=20)
