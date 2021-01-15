import unittest
from datetime import date, datetime
from decimal import Decimal

from banking.domain import Account, Transaction


class TestAccountAndTransactionIntegration(unittest.TestCase):
    def setUp(self):
        self.transaction = Transaction.new()
        self.account = Account.new()

    def test_should_be_possible_append_new_transaction_to_account(self):
        self.account.add_transaction(self.transaction)
        self.assertEqual(1, len(self.account.transactions))

    def test_should_not_be_possible_add_other_type_of_class_in_the_transactions_list(
        self,
    ):
        with self.assertRaisesRegex(
            TypeError, "Could not add the object '\{\}' to the transaction list"
        ):
            self.account.add_transaction({})
