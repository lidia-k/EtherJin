from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch_dsl import Index

from etherscan_app.indexes import FolderDocument


class Command(BaseCommand):
    def handle(self, *args, **options):
        index = Index(settings.ELASTICSEARCH_INDEX)
        index.document(FolderDocument)
        index.create()
        self.stdout.write(self.style.SUCCESS(f"{index} index successfully created!"))
