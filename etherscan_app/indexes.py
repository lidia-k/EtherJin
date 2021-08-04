from elasticsearch_dsl import Document, Long, Text
import logging

logger = logging.getLogger(__name__)


class FolderDocument(Document):
    name = Text(analyzer="english")
    id = Long()

    @classmethod
    def from_folder(self, folder):
        doc = self(id=folder.pk, name=folder.name)
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


class AddressDocument(Document):
    address = Text(analyzer="english")

    @classmethod
    def from_address(self, address):
        import pdb;pdb.set_trace()
        doc = self(address=address.address)
        doc.meta.id = f"ADDRESS-{address.pk}"
        doc.save()

    class Index:
        name = 'etherjin'


def update_address_document(address):
    from etherscan_app.models import Address

    address = Address.objects.filter(address=address).first()
    if address:
        logger.info(f"Updating the index for {address}")
        AddressDocument.from_address(address)