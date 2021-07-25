from django.db.models.signals import post_save
from django.dispatch import receiver
from etherscan_app.models import Address
from django_q.tasks import async_task
from etherscan_app.utils import validate_address

@receiver([post_save], sender=Address)
def create_transactions(sender, instance, created, using, update_fields, **kwargs):
    pk = instance.pk
    _, response_data = validate_address(instance.pk)
    async_task('etherscan_app.utils.create_transaction', pk, response_data['result'])