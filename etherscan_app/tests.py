from django.test import TestCase, Client
from etherscan_app.utils import validate_address, create_address, create_transaction
from etherscan_app.models import Address
from etherscan_app.views import show_results
from django.db.utils import IntegrityError 
from django.urls import reverse

class ValidateAddressTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('results') 

    def test_validate_address_with_valid_address(self):
        """
        validate_address() returns True for a valid address 
        """
        address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        valid_address, response_data = validate_address(address)
        self.assertTrue(valid_address)

    def test_validate_address_with_invalid_address(self):
        """
        validate_address() returns False for an invalid address
        """
        address = "1234567890aaazzz"
        valid_address, response_data = validate_address(address)
        response = self.client.post(self.url, {'address': address})
        self.assertFalse(valid_address)
        self.assertEqual(response.status_code, 400)
class CreateAddressTests(TestCase):
    def setUp(self):
        self.address = "0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF"
        self.address_instance = Address.objects.create(address=self.address)
    
    def test_create_address_with_valid_address(self):
        new_address = '0x8d7c9AE01050a31972ADAaFaE1A4D682F0f5a5Ca'
        create_address(new_address)
        self.assertEqual(Address.objects.last().address, new_address)

    def test_create_address_with_already_existing_address(self):
        address_instance = create_address(self.address)
        self.assertEqual(address_instance, None)

class CreateTransactionTests(TestCase):
    def setUp(self):
        address = "0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF"
        self.address_instance = create_address(address)
        valid_address, response_data = validate_address(address)
        self.result_data = response_data['result']
    
    def test_create_transaction_with_new_address(self):
        create_transaction(self.address_instance, self.result_data)
        transactions = Address.objects.last().transactions.all()
        self.assertTrue(transactions)

class UpdateTransactionTests(TestCase):
    pass
