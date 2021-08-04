from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.db.models import signals
from django.test import Client, TestCase
from django.urls import reverse

from requests.models import Response

from etherscan_app.cron import update_transactions
from etherscan_app.models import (Address, AddressUserRelationship, Folder,
                                  Transaction)
from etherscan_app.utils import (create_or_update_transaction,
                                 get_address_response)


@patch("etherscan_app.utils.requests.get")
class ValidateAddressTests(TestCase):
    def setUp(self):
        self.res = Mock(spec=Response)
        self.user_instance = User.objects.create(username="testuser")

    def test_validate_address_with_valid_address(self, request_patch):
        """
        Tests validate_address returns True when taking in a valid address
        """
        patched_data = {"status": "1", "message": "OK", "result": "result data"}
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
            "status": "0",
            "message": "NOTOK",
            "result": "Error! Invalid address format",
        }
        self.res.json.return_value = patched_data
        request_patch.return_value = self.res

        address = "1234567890aaazzz"
        valid_address, response_data = validate_address(address)

        self.assertFalse(valid_address)
        self.assertEqual(response_data["result"], "Error! Invalid address format")


@patch("etherscan_app.views.validate_address")
class SubmitAddressTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("etherscan_app:submit-address")
        self.user_instance = User.objects.create(username="testuser")
        signals.post_save.receivers = []

    def test_submit_address_with_valid_address(self, validate_address_patch):
        """
        Tests submit_address successfully creates an address instance with a valid address
        """
        patched_data = {"status": "1", "message": "OK", "result": "result data"}
        validate_address_patch.return_value = True, patched_data
        address = "0x8d7c9AE01050a31972ADAaFaE1A4D682F0f5a5Ca"

        self.client.force_login(self.user_instance)
        self.client.post(self.url, {"address": address})
        address_instance = Address.objects.get(address=address)

        self.assertEqual(Address.objects.latest("created_at").address, address)
        self.assertTrue(
            AddressUserRelationship.objects.filter(
                user=self.user_instance, address=address_instance
            )
        )

    def test_submit_address_with_invalid_address(self, validate_address_patch):
        """
        Tests submit_address throws 400 error when taking in an invalid address
        """
        patched_data = {
            "status": "0",
            "message": "NOTOK",
            "result": "Error! Invalid address format",
        }
        validate_address_patch.return_value = False, patched_data

        address = "1234567890aaazzz"
        self.client.force_login(self.user_instance)
        response = self.client.post(self.url, {"address": address})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), patched_data["result"])

    def test_submit_address_with_other_errors(self, validate_address_patch):
        """
        Tests submit_address throws 400 error when receiving errors from the API
        """
        address = "0x8d7c9AE01050a31972ADAaFaE1A4D682F0f5a5Ca"
        patched_data = {
            "status": "1",
            "message": "OK-Missing/Invalid API Key, rate limit of 1/5sec applied",
            "result": "595623370144773018344492",
        }
        validate_address_patch.return_value = False, patched_data

        self.client.force_login(self.user_instance)
        response = self.client.post(self.url, {"address": address})

        self.assertEqual(response.status_code, 400)


class CreateTransactionTests(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.address_instance = Address.objects.create(
            address="0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF"
        )
        self.transaction_data = [
            {
                "hash": "0xmyhash",
                "from": "0xfromaccount",
                "to": "0xtoaccount",
                "value": "0.0000000001",
            }
        ]
        self.response_data = {
            "status": "1",
            "message": "OK",
            "result": self.transaction_data,
        }

    def test_create_transaction_with_new_address(self):
        """
        Takes in a new valid address
        Creates transaction instances of the given address
        """
        result_data = self.response_data["result"]
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
            "to_account": "0xtoaccount",
            "value_in_ether": 0.0000000001,
        }
        Transaction.objects.create(**fields)
        transaction_count = Transaction.objects.filter(
            address=self.address_instance
        ).count()

        new_data = {
            "hash": "0xanotherhash",
            "from": "0xfromaccount",
            "to": "0xtoaccount",
            "value": "0.0000000001",
        }
        self.transaction_data.append(new_data)
        result_data = self.response_data["result"]
        create_or_update_transaction(self.address_instance.pk, result_data)

        self.assertTrue(
            transaction_count
            < Transaction.objects.filter(address=self.address_instance).count()
        )


class ResultsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_instance = User.objects.create(username="testuser")
        signals.post_save.receivers = []

    def test_results_view_with_valid_address(self):
        """
        Takes in a valid address
        Renders 'results.html' template with the address as context
        """
        address = "0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF"
        Address.objects.create(address=address)

        url = reverse("etherscan_app:results", kwargs={"address": address})
        self.client.force_login(self.user_instance)
        res = self.client.get(url)
        context_address = res.context.get("address")

        self.assertEqual(context_address, Address.objects.last().pk)


class FolderRelatedTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="testuser")

        signals.post_save.receivers = []
        self.address = "0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF"
        self.address_instance = Address.objects.create(address=self.address)
        self.address_instance.users.add(self.user)

        self.folder_name = "test_folder"
        self.folders = ["test1", "test2", "test3"]

    def test_save_address_to_folder(self):
        folder = Folder.objects.create(user=self.user, folder_name=self.folder_name)

        url = reverse("etherscan_app:save-address-to-folder")
        self.client.force_login(self.user)
        self.client.post(url, {"address": self.address, "folder": folder.pk})

        self.assertTrue(folder.addresses.get(address=self.address))

    def test_create_folder_without_saved_address(self):
        url = reverse("etherscan_app:create-folder")

        self.client.force_login(self.user)
        self.client.post(url, {"folder": self.folder_name})

        self.assertEqual(self.folder_name, Folder.objects.last().folder_name)

    def test_create_folder_with_saved_address(self):
        url = reverse("etherscan_app:create-folder")
        self.client.force_login(self.user)
        self.client.post(url, {"folder": self.folder_name, "address": self.address})
        self.assertEqual(Folder.objects.last().addresses.get().address, self.address)

    def test_show_folders(self):
        for folder in self.folders:
            Folder.objects.create(user=self.user, folder_name=folder)

        url = reverse("etherscan_app:show-folders")
        self.client.force_login(self.user)
        res = self.client.get(url)
        context_lists = [x.folder_name for x in res.context.get("folders")]
        self.assertEqual(
            context_lists, [x.folder_name for x in self.user.folders.all()]
        )

    def test_show_folder(self):
        folder = Folder.objects.create(user=self.user, folder_name=self.folder_name)
        self.address_instance.folders.add(folder)

        url = reverse("etherscan_app:show-folder", kwargs={"folder_id": folder.pk})
        self.client.force_login(self.user)
        res = self.client.get(url)

        self.assertEqual(res.context.get("folder"), folder)
        self.assertEqual(
            res.context.get("address_user_instances")[0],
            AddressUserRelationship.objects.get(
                user=self.user, address=self.address_instance
            ),
        )

    def test_edit_folder_name(self):
        folder = Folder.objects.create(user=self.user, folder_name=self.folder_name)
        url = reverse("etherscan_app:edit-folder-name", kwargs={"folder_id": folder.pk})
        new_name = "new_name"

        self.client.force_login(self.user)
        self.client.post(url, {"folder_name": new_name})

        self.assertEqual(Folder.objects.get(pk=folder.pk).folder_name, new_name)

    def test_delete_list(self):
        for folder in self.folders:
            Folder.objects.create(user=self.user, folder_name=folder)

        url = reverse("etherscan_app:delete-folder", kwargs={"folder_id": 1})

        self.client.force_login(self.user)
        self.client.get(url)

        self.assertEqual(Folder.objects.all().count(), 2)


@patch("etherscan_app.signals.validate_address")
class AddressSignalsTest(TestCase):
    def test_create_transactions_with_saved_address(self, function_patch):
        response_data = {"status": "1", "message": "OK", "result": "result"}
        function_patch.return_value = True, response_data
        address = "0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF"
        Address.objects.create(address=address)

        self.assertTrue(function_patch.called)


class CronJobFunctionTest(TestCase):
    @patch("etherscan_app.cron.create_or_update_transaction")
    @patch("etherscan_app.cron.get_address_response")
    def test_update_transactions(
        self, get_address_response_patch, create_or_update_transaction_patch
    ):
        signals.post_save.receivers = []

        addresses = [
            "0xD4fa6E82c77716FA1EF7f5dEFc5Fd6eeeFBD3bfF",
            "0x8d7c9AE01050a31972ADAaFaE1A4D682F0f5a5Ca",
        ]
        for address in addresses:
            Address.objects.create(address=address)
        get_address_response_patch.return_value = True, {
            "status": "1",
            "message": "OK",
            "result": "result",
        }
        update_transactions()

        self.assertTrue(get_address_response_patch.called)
