from unittest.mock import patch

from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from apps.bank.models import BankAccount
from apps.stores.models import InventoryItem, Product, Store
from apps.utils.models import UsageReceipt
from apps.users.models import CustomUser
from apps.users.services import use_inventory_item


class UseInventoryItemTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='owner', password='test-password', full_name='Owner')
        self.other_user = CustomUser.objects.create_user(
            username='other', password='test-password', full_name='Other')
        BankAccount.objects.create(user=self.user)
        self.store = Store.objects.create(name='Test Store', description='')
        self.product = Product.objects.create(
            name='Test Wand',
            description='',
            price=10,
            store=self.store,
            product_type='wand',
            duration_days=30,
            uses=2,
            stackable=True,
        )
        self.item = InventoryItem.objects.create(
            user=self.user,
            product=self.product,
            store=self.store,
            uses=2,
        )

    def test_use_creates_receipt_with_remaining_uses(self):
        receipt = use_inventory_item(self.item.id, self.user)

        self.item.refresh_from_db()
        self.assertEqual(self.item.uses, 1)
        self.assertEqual(receipt.uses_left, 1)
        self.assertEqual(receipt.user, self.user)

    def test_receipt_failure_rolls_back_use(self):
        with patch(
            'apps.users.services.utils.generate_usage_receipt',
            side_effect=RuntimeError,
        ):
            with self.assertRaises(RuntimeError):
                use_inventory_item(self.item.id, self.user)

        self.item.refresh_from_db()
        self.assertEqual(self.item.uses, 2)
        self.assertEqual(UsageReceipt.objects.count(), 0)

    def test_user_cannot_consume_another_users_item(self):
        with self.assertRaises(Http404):
            use_inventory_item(self.item.id, self.other_user)

        self.item.refresh_from_db()
        self.assertEqual(self.item.uses, 2)

    def test_post_redirects_to_recoverable_usage_receipt(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('profile'), {'item_id': self.item.id})

        receipt = UsageReceipt.objects.get(user=self.user)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            f"{reverse('profile')}?usage_receipt={receipt.code}#inventory",
        )

        response = self.client.get(
            reverse('profile'), {'usage_receipt': receipt.code})
        self.assertContains(response, receipt.code)

        response = self.client.get(reverse('receipts'))
        self.assertContains(
            response,
            f'href="{reverse("profile")}?usage_receipt={receipt.code}#inventory"',
        )
