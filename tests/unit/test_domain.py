import unittest
from decimal import Decimal

from banking.domain import Person, Transaction, Account


class TestPersonDomaiin(unittest.TestCase):
    def setUp(self):
        self.person = Person.new()

    def test_should_create_a_default_instance(self):
        self.assertEqual(None, self.person.id)
        self.assertEqual(None, self.person.name)
        self.assertEqual(None, self.person.cpf)
        self.assertEqual(None, self.person.born_at)

    def test_the_method_new_should_be_static(self):
        self.assertEqual(type(Person.__dict__["new"]), staticmethod)


class TestTransactionDomain(unittest.TestCase):
    def setUp(self):
        self.transaction = Transaction.new()

    def test_should_create_a_default_instance(self):
        self.assertEqual(None, self.transaction.id)
        self.assertEqual(None, self.transaction.account_id)
        self.assertEqual(None, self.transaction.value)
        self.assertEqual(None, self.transaction.created_at)


class TestAccountDomain(unittest.TestCase):
    def setUp(self):
        self.account = Account.new()

    def test_should_create_a_default_instance(self):
        self.assertIsNone(self.account.id)
        self.assertEqual(Decimal("0"), self.account.balance)
        self.assertEqual(Decimal("1000"), self.account.daily_withdrawal_limit)
        self.assertEqual(1, self.account.type)
        self.assertEqual(True, self.account.active)
        self.assertEqual([], self.account.transactions)
        self.assertEqual(None, self.account.person_id)

    def test_the_method_new_should_be_static(self):
        self.assertEqual(type(Account.__dict__["new"]), staticmethod)

    def test_should_be_possible_to_deactivate_the_account(self):
        self.assertTrue(self.account.active)
        self.account.block()
        self.assertFalse(self.account.active)

    def test_should_be_possible_to_reactivate_the_account(self):
        self.assertTrue(self.account.active)
        self.account.block()
        self.assertFalse(self.account.active)
        self.account.unblock()
        self.assertTrue(self.account.active)
