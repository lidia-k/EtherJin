from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.db.models import signals

from requests.models import Response

from etherscan_app.models import Address, Folder, Transaction
from etherscan_app.utils import create_or_update_transaction, validate_address


@patch('etherscan_app.utils.requests.get')
class ValidateAddressTests(TestCase):
    def setUp(self):
        self.res = Mock(spec=Response)
        self.user_instance = User.objects.create(username='testuser')

    def test_validate_address_with_valid_address(self, request_patch):
        """
        Tests validate_address returns True when taking in a valid address
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
        Tests validate_address return False when taking in an invalid address
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

@patch('etherscan_app.views.validate_address')
class SubmitAddressTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('etherscan_app:submit-address')
        self.user_instance = User.objects.create(username='testuser')
        signals.post_save.receivers = []
    
    def test_submit_address_with_valid_address(self, validate_address_patch):
        """
        Tests submit_address successfully creates an address instance with a valid address 
        """
        patched_data = {
            "status":"1",
            "message":"OK",
            "result":"result data"
        }
        validate_address_patch.return_value = True, patched_data

        address = '0x8d7c9AE01050a31972ADAaFaE1A4D682F0f5a5Ca'
        self.client.force_login(self.user_instance)
        self.client.post(self.url, {'address': address})
        self.assertEqual(Address.objects.latest('created_at').address, address)

    def test_submit_address_with_invalid_address(self, validate_address_patch):
        """
        Tests submit_address throws 400 error when taking in an invalid address
        """
        patched_data = {
            "status":"0",
            "message":"NOTOK",
            "result":"Error! Invalid address format"
            }
        validate_address_patch.return_value = False, patched_data
        
        address = '1234567890aaazzz'
        self.client.force_login(self.user_instance)
        response = self.client.post(self.url, {'address': address})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), patched_data['result'])

    def test_submit_address_with_other_errors(self, validate_address_patch):
        """
        Tests submit_address throws 400 error when receiving errors from the API
        """
        address = '0x8d7c9AE01050a31972ADAaFaE1A4D682F0f5a5Ca'
        patched_data = {
            "status":"1",
            "message":"OK-Missing/Invalid API Key, rate limit of 1/5sec applied",
            "result":"595623370144773018344492"}
        validate_address_patch.return_value = False, patched_data

        self.client.force_login(self.user_instance)
        response = self.client.post(self.url, {'address': address})

        self.assertEqual(response.status_code, 400)

class CreateTransactionTests(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.address_instance = Address.objects.create(address="0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF")
        self.transaction_data = [{
            "hash": "0xmyhash",
            "from": "0xfromaccount",
            "to":"0xtoaccount",
            "value": "0.0000000001",
        }]
        self.response_data = {
            "status":"1",
            "message":"OK",
            "result": self.transaction_data
        }
        
    def test_create_transaction_with_new_address(self):
        """
        Takes in a new valid address
        Creates transaction instances of the given address
        """
        result_data = self.response_data['result']
        create_or_update_transaction(self.address_instance.pk, result_data)
        transactions = Transaction.objects.filter(address=self.address_instance)
        self.assertTrue(transactions)

    def test_update_transaction_with_existing_address(self):
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
        result_data = self.response_data['result']
        create_or_update_transaction(self.address_instance.pk, result_data)
       
        self.assertTrue(transaction_count < Transaction.objects.filter(address=self.address_instance).count())

class ResultsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_instance = User.objects.create(username='testuser')
        signals.post_save.receivers = []

    def test_results_view_with_valid_address(self):    
        """
        Takes in a valid address
        Renders 'results.html' template with the address as context
        """
        address = '0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF'
        Address.objects.create(address=address)

        url = reverse('etherscan_app:results', kwargs={'address': address})
        self.client.force_login(self.user_instance)
        res = self.client.get(url)
        context_address = res.context.get('address')
       
        self.assertEqual(context_address, Address.objects.last().pk)
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

class FolderRelatedTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser')
        self.lists = ['test1', 'test2', 'test3']

    def test_save_address_to_folder(self):
        address = '0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF'
        address_instance = Address.objects.create(address=address)
        address_instance.users.add(self.user)
        folder_name = 'test_folder'
        folder = Folder.objects.create(user=self.user, folder_name=folder_name)

        url = reverse('etherscan_app:save-address-to-folder')
        self.client.force_login(self.user)
        self.client.post(url, {'address': address, 'folder': folder_name})
        
        self.assertTrue(folder.addresses.get(address=address))

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

@patch('etherscan_app.signals.validate_address')
class AddressSignalsTest(TestCase):
    def test_create_transactions_with_saved_address(self, function_patch):
        response_data = {
            "status":"1",
            "message":"OK",
            "result": "result"
        }
        function_patch.return_value = True, response_data
        address = '0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF'
        Address.objects.create(address=address)

        self.assertTrue(function_patch.called)
