import logging

from elasticsearch_dsl import Document, Long, Text

logger = logging.getLogger(__name__)


class FolderDocument(Document):
    folder_name = Text(analyzer="english")
    id = Long()

    @classmethod
    def from_folder(self, folder):
        doc = self(id=folder.pk, folder_name=folder.folder_name)
        doc.meta.id = f"FOLDER-{folder.pk}"
        doc.save()

    class Index:
        name = "etherjin"


def update_folder_document(folder_id):
    from etherscan_app.models import Folder

    folder = Folder.objects.filter(pk=folder_id).first()
    if folder:
        logger.info("Updating the index for {folder}")
        FolderDocument.from_folder(folder)


def delete_folder_document(folder_id):
    doc = FolderDocument()
    doc.meta.id = f"FOLDER-{folder_id}"
    doc.delete(ignore=404)
