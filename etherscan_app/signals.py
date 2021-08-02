from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from etherscan_app.models import Address, Folder
from django_q.tasks import async_task
from etherscan_app.utils import get_address_response

import logging

logger = logging.getLogger(__name__)

@receiver([post_save], sender=Address)
def create_transactions(sender, instance, created, using, update_fields, **kwargs):
    pk = instance.pk
    _, response_data = get_address_response(instance.pk)
    async_task('etherscan_app.utils.create_or_update_transaction', pk, response_data['result'])

@receiver([post_save], sender=Folder)
def folder_saved(sender, instance, created, using, update_fields, **kwargs):
    logger.info(f'Folder {instance} is being added')
    async_task('etherscan_app.indexes.update_folder_document', instance.id)

@receiver([post_delete], sender=Folder)
def folder_saved(sender, instance, created, using, update_fields, **kwargs):
    logger.info(f'Folder {instance} is being deleted')
    async_task('etherscan_app.indexes.delete_folder_document', instance.id)

