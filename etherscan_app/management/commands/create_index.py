
from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch_dsl import Index

from etherscan_app.indexes import FolderDocument
from etherscan_app.models import Folder


class Command(BaseCommand):
    def handle(self, *args, **options):
        index = Index(settings.ELASTICSEARCH_INDEX)
        index.delete(ignore=404)
        index.document(FolderDocument)
        index.create()
        [FolderDocument.from_folder(folder) for folder in Folder.objects.all()]
        self.stdout.write(self.style.SUCCESS(f"{index} index successfully created!"))
