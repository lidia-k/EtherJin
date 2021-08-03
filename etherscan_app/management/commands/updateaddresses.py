import os

from django.core.management.base import BaseCommand, CommandError

from etherscan_app.models import Address
from etherscan_app.utils import (create_or_update_transaction,
                                 get_address_response)


class Command(BaseCommand):
    help = "Update the saved addresses with their transaction data"

    def handle(self, *args, **options):
        if not os.getenv("ETHERSCAN_API_TOKEN"):
            raise CommandError("API_TOKEN isn't provided")

        addresses_list = Address.objects.all()
        for address_obj in addresses_list:
            address = address_obj.pk
            _, response_data = get_address_response(address)
            result_data = response_data["result"]
            create_or_update_transaction(address, result_data)
            self.stdout.write(self.style.SUCCESS(f"{address} is successfully updated."))
