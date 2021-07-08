from unittest.mock import patch, Mock

from requests.models import Response
from django.test import Client, TestCase
from django.urls import reverse

from etherscan_app.models import Address, Transaction
from etherscan_app.utils import create_transaction, validate_address

@patch('etherscan_app.utils.requests.get')
class ValidateAddressTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('results') 
        self.res = Mock(spec=Response)

    def test_validate_address_with_valid_address(self, request_patch):
        """
        Takes in a valid address
        validate_address() returns True 
        """
        patched_data = {
            "status":"1",
            "message":"OK",
            "result":"result data"
            }
        self.res.json.return_value = patched_data
        request_patch.return_value = self.res
 
        address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        valid_address, _ = validate_address(address)
        self.assertTrue(valid_address)

    def test_validate_address_with_invalid_address(self, request_patch):
        """
        Takes in an invalid address
        validate_address() returns False 
        """
        patched_data = {
            "status":"0",
            "message":"NOTOK",
            "result":"Error! Invalid address format"
            }
        self.res.json.return_value = patched_data
        request_patch.return_value = self.res
        
        address = "1234567890aaazzz"
        valid_address, response_data = validate_address(address)

        self.assertFalse(valid_address)
        self.assertEqual(response_data['result'], "Error! Invalid address format")

    def test_results_view_with_invalid_address(self, request_patch):
        """
        Takes in an invalid address
        'results' view returns 400  
        """
        patched_data = {
            "status":"0",
            "message":"NOTOK",
            "result":"Error! Invalid address format"
            }
        self.res.json.return_value = patched_data
        request_patch.return_value = self.res
    
        address = "1234567890aaazzz"
        response = self.client.post(self.url, {'adress': address})

        self.assertEqual(response.status_code, 400)
class CreateAddressTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('results')
        self.address = '0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF'
        self.address_instance = Address.objects.create(address=self.address)
        self.res = Mock(spec = Response)
    
    @patch('etherscan_app.utils.requests.get')
    def test_create_address_with_new_address(self, request_patch):
        """
        Takes in a new valid address
        Creates an address instance
        """
        patched_data = {
            "status":"1",
            "message":"OK",
            "result":"result data"
        }
        self.res.json.return_value = patched_data
        request_patch.return_value = self.res

        new_address = '0x8d7c9AE01050a31972ADAaFaE1A4D682F0f5a5Ca'
        self.client.post(self.url, {'address': new_address})
        self.assertEqual(Address.objects.latest('created_at').address, new_address)

class CreateTransactionTests(TestCase):
    @patch('etherscan_app.utils.requests.get')
    def setUp(self, request_patch):
        self.request_patch = request_patch
        self.client = Client()
        self.url = reverse('results')
        self.address_instance = Address.objects.create(address="0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF")
        self.transaction_data = {
            "address": self.address_instance.pk,
            "hash": "0xmyhash",
            "from_account": "0xfromaccount",
            "to_account":"0xtoaccount",
            "value_in_ether": "0.0000000001",
        }
        
    def test_create_transaction_with_new_address(self):
        """
        Takes in a new valid address
        Creates transaction instances of the given address
        """
        self.request_patch.return_value = HttpResponse({
            "status":"1",
            "message":"OK",
            "result": self.transaction_data
        })
        _, response_data = validate_address(self.address_instance.pk)
        result_data = response_data['result']
        create_transaction(self.address_instance, result_data)
        transactions = Transaction.objects.filter(address=self.address_instance)
        self.assertTrue(transactions)

    def test_create_transaction_with_existing_address(self):
        """
        Takes in an existing address
        Updates the transaction table with the new data 
        """
        fields = {
            "address": self.address_instance, 
            "hash": "0xmyhash",
            "from_account": "0xfromaccount",
            "to_account":"0xtoaccount",
            "value_in_ether": 0.0000000001,
        }
        Transaction.objects.create(**fields)

        transaction_count = Transaction.objects.filter(address=self.address_instance).count()
        new_data = [self.transaction_data, 
            {
                "address": self.address_instance.pk, 
                "hash": "0xmyhash",
                "from_account": "0xfromaccount",
                "to_account":"0xtoaccount",
                "value_in_ether": "0.0000000001",
            }
        ]
        self.request_patch.return_value = HttpResponse({
            "status":"1",
            "message":"OK",
            "result": new_data
        })
        _, response_data = validate_address(self.address_instance.pk)
        result_data = response_data['result']
        create_transaction(self.address_instance, result_data)
       
        self.assertTrue(transaction_count < Transaction.objects.filter(address=self.address_instance).count())

