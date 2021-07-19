from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from requests.models import Response

from etherscan_app.models import Address, Folder, Transaction
from etherscan_app.utils import create_transaction, validate_address


@patch('etherscan_app.utils.requests.get')
class ValidateAddressTests(TestCase):
    def setUp(self):
        self.res = Mock(spec=Response)
        self.user_instance = User.objects.create(username='testuser')

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

class CreateAddressTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('etherscan_app:submit-address')
        self.address = '0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF'
        self.address_instance = Address.objects.create(address=self.address)
        self.res = Mock(spec = Response)
        self.user_instance = User.objects.create(username='testuser')
    
    @patch('etherscan_app.views.async_task')
    @patch('etherscan_app.utils.requests.get')
    def test_create_address_with_new_address(self, request_patch, async_task_patch):
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
        self.client.force_login(self.user_instance)
        self.client.post(self.url, {'address': new_address})
        self.assertEqual(Address.objects.latest('created_at').address, new_address)

@patch('etherscan_app.utils.requests.get')
class CreateTransactionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('etherscan_app:results')
        self.res = Mock(spec=Response)
        self.address_instance = Address.objects.create(address="0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF")
        self.transaction_data = [{
            "hash": "0xmyhash",
            "from": "0xfromaccount",
            "to":"0xtoaccount",
            "value": "0.0000000001",
        }]
        
    def test_create_transaction_with_new_address(self, request_patch):
        """
        Takes in a new valid address
        Creates transaction instances of the given address
        """
        self.res.json.return_value = {
            "status":"1",
            "message":"OK",
            "result": self.transaction_data
        }
        request_patch.return_value = self.res
        _, response_data = validate_address(self.address_instance.pk)
        result_data = response_data['result']
        create_transaction(self.address_instance.pk, result_data)
        transactions = Transaction.objects.filter(address=self.address_instance)
        self.assertTrue(transactions)

    def test_create_transaction_with_existing_address(self, request_patch):
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
        new_data = {
            "hash": "0xanotherhash",
            "from": "0xfromaccount",
            "to":"0xtoaccount",
            "value": "0.0000000001",
        }
        self.transaction_data.append(new_data)
        self.res.json.return_value = {
            "status":"1",
            "message":"OK",
            "result": self.transaction_data
        }
        request_patch.return_value = self.res
        _, response_data = validate_address(self.address_instance.pk)
        result_data = response_data['result']
        create_transaction(self.address_instance.pk, result_data)
       
        self.assertTrue(transaction_count < Transaction.objects.filter(address=self.address_instance).count())

@patch('etherscan_app.views.validate_address')
class ResultsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('etherscan_app:results')
        self.user_instance = User.objects.create(username='testuser')

    @patch('etherscan_app.views.async_task')    
    def test_results_view_with_valid_address(self, async_task_patch, validate_address_patch):    
        """
        Takes in a valid address
        Renders 'results.html' template with the address as context
        """
        response_data = {
            "status":"1",
            "message":"OK",
            "result":"result data"
        }
        validate_address_patch.return_value = True, response_data
        
        self.client.force_login(self.user_instance)
        address = '0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF'
        res = self.client.get(self.url, {'address': address})
        context_address = res.context.get('address')
       
        self.assertEqual(context_address, Address.objects.last().pk)

    def test_results_view_with_invalid_address(self, validate_address_patch):
        """
        Takes in an invalid address
        'results' view returns 400  
        """
        response_data = {
            "status":"0",
            "message":"NOTOK",
            "result":"Error! Invalid address format"
        }
        validate_address_patch.return_value = False, response_data
    
        address = "1234567890aaazzz"
        self.client.force_login(self.user_instance)
        response = self.client.get(self.url, {'adress': address})

        self.assertEqual(response.status_code, 400)  
class UserAddressesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('etherscan_app:user_addresses')
        self.user_instance = User.objects.create(username='testuser')

    def test_show_user_addresses_view_with_addresses(self):
        addresses = [
            '0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF', 
            '0x8d7c9AE01050a31972ADAaFaE1A4D682F0f5a5Ca',]
        
        for address in addresses:
            address_instance = Address.objects.create(address=address)
            address_instance.users.add(self.user_instance)

        self.client.force_login(self.user_instance)
        res = self.client.get(self.url)
        
        context_addresses = [x.address for x in res.context.get('addresses')]
        self.assertEqual(context_addresses, [x.address for x in self.user_instance.addresses.all()])

    def test_show_user_address_view_without_addresses(self):
        self.client.force_login(self.user_instance)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

class ListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser')
        self.lists = ['test1', 'test2', 'test3']

    def test_create_list(self):
        self.client.force_login(self.user)
        url = reverse('etherscan_app:create_list')
        list_name = 'test_list'
        self.client.post(url, {'list_name': list_name})
        self.assertEqual(list_name, Folder.objects.last().folder)

    def test_retrieve_lists(self):
        for list in self.lists: 
            Folder.objects.create(user=self.user, folder=list)

        url = reverse('etherscan_app:show_lists')
        self.client.force_login(self.user)
        res = self.client.get(url)
        context_lists = [x.folder for x in res.context.get('lists')]
        self.assertEqual(context_lists, [x.folder for x in self.user.folders.all()])

    def test_update_list(self):
        pass
        """
        for list in self.lists: 
            Folder.objects.create(user=self.user, folder=list)

        updated_lists = {'test1', 'test2', ''}

        self.client.force_login(self.user)
        url = reverse('etherscan_app:update_list')
        list = self.client.get(url, {'list': })

        self.client.post(url, {'list': ''})
        """

    def test_delete_list(self):
        pass