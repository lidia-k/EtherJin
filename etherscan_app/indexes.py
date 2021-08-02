from elasticsearch_dsl import Document, Long, Text
import logging

logger = logging.getLogger(__name__)

class FolderDocument(Document):
    folder_name = Text(analyzer='english')
    id = Long()

    @classmethod
    def from_folder(self, folder):
        doc = self(id=folder.id, folder_name=folder.folder_name)
        doc.meta.id  = f'FOLDER-{folder.id}'

        return doc

    class Index:
        name = 'etherjin'

def update_folder_document(folder_id):
    from etherscan_app.models import Folder
    folder = Folder.objects.filter(id=folder_id).first()
    if folder:
        logger.info(f'Updating index for folder {folder}')
        doc = FolderDocument.from_folder(folder)
        doc.save()

def delete_folder_document(folder_id):
    doc = FolderDocument()
    doc.meta.id = f'FOLDER-{folder_id}'
    doc.delete(ignore=404)
