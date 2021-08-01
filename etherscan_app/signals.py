from django.db.models.signals import post_save
from django.dispatch import receiver
from etherscan_app.models import Address
from django_q.tasks import async_task
from etherscan_app.utils import get_address_response

@receiver([post_save], sender=Address)
def create_transactions(sender, instance, created, using, update_fields, **kwargs):
    pk = instance.pk
    _, response_data = get_address_response(instance.pk)
    async_task('etherscan_app.utils.create_or_update_transaction', pk, response_data['result'])