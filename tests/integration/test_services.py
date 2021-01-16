import unittest
from datetime import datetime, timedelta
from random import randint
from decimal import Decimal
from time import sleep

from banking import exceptions
from banking.adapters import SqlUnitOfWork
from banking.domain import Account
from banking.services import get_commands
from tests import DatabaseInMemoryMixin, create_person


class TestAccountCreateService(DatabaseInMemoryMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.unit_of_work = SqlUnitOfWork(self.session_factory)
        self.command = get_commands(self.unit_of_work)["account_register"]
        self.account_id = randint(1, 1000)

        with self.unit_of_work as uow:
            uow.people.add(create_person(id=self.account_id))

    def test_should_be_possible_to_register_a_new_account(self):
        account = self.command(person_id=self.account_id, type_id=1)
        self.assertTrue(isinstance(account, Account))

    def test_should_raise_an_exception_if_an_account_does_not_exists(self):
        with self.assertRaises(exceptions.DoesNotExist):
            self.command(person_id=10001, type_id=1)


class TestAccountDepositValueService(DatabaseInMemoryMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.unit_of_work = SqlUnitOfWork(self.session_factory)
        self.command = get_commands(self.unit_of_work)["account_deposit"]
        self.person_id = randint(1, 1000)

        register_command = get_commands(self.unit_of_work)["account_register"]

        with self.unit_of_work as uow:
            person = create_person(id=self.person_id)
            uow.people.add(person)

        with self.unit_of_work as uow:
            self.account = register_command(person_id=self.person_id, type_id=1)

    def test_the_account_balance_should_deposit_a_value(self):
        actual_balance = self.account.balance
        account = self.command(self.account.id, Decimal("30"))
        self.assertEqual(account.balance, actual_balance + 30)

    def test_should_raise_an_exception_if_an_account_does_not_exists(self):
        with self.assertRaises(exceptions.DoesNotExist):
            self.command(id=8000, value=1)

    def test_should_raise_an_exception_if_the_value_is_non_numerical(self):
        with self.assertRaisesRegex(
            ValueError,
            "Could not deposit the amount '@' because it isn't a valid value",
        ):
            self.command(id=self.account.id, value="@")


class TestAccountFetchService(DatabaseInMemoryMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.unit_of_work = SqlUnitOfWork(self.session_factory)

        with self.unit_of_work as uow:
            account = Account.new()
            account.id = 1
            account.person_id = 1
            uow.accounts.add(account)

        self.command = get_commands(self.unit_of_work)["account_fetch"]

    def test_should_be_possible_obtain_an_existing_account_by_id(self):
        account = self.command(1)
        self.assertIsNotNone(account)

    def test_should_raise_does_not_exist_exception_if_an_account_was_not_found(self):
        with self.assertRaisesRegex(exceptions.DoesNotExist, "^Does not exist$"):
            self.command(2)


class TestAccountWithddrawValueService(DatabaseInMemoryMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.unit_of_work = SqlUnitOfWork(self.session_factory)

        with self.unit_of_work as uow:
            account = Account.new()
            account.id = 1
            account.person_id = 1
            account.balance = Decimal("100.00")
            uow.accounts.add(account)

        self.command = get_commands(self.unit_of_work)["account_withdraw"]

    def test_should_be_possible_withdraw_10_units_from_an_account(self):
        account = self.command(1, "11.01")
        self.assertEqual(account.balance, Decimal("88.99"))

    def test_when_an_withdraw_were_made_it_should_produce_an_transaction(self):
        account = self.command(1, "50.00")
        self.assertEqual(len(account.transactions), 1)

    def test_transactions_should_have_the_withdraw_type_when_their_are_made_by_this_command(
        self,
    ):
        self.command(1, "50.00")
        account = self.command(1, "50.00")

        for transaction in account.transactions:
            self.assertEqual(transaction.type, "withdraw")


class TestAccountBlockService(DatabaseInMemoryMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.unit_of_work = SqlUnitOfWork(self.session_factory)

        with self.unit_of_work as uow:
            account = Account.new()
            account.id = 1
            account.person_id = 1
            uow.accounts.add(account)

        self.command = get_commands(self.unit_of_work)["account_block"]

    def test_should_set_an_account_active_status_as_false(self):
        account = self.command(1)
        self.assertEqual(account.active, False)


class TestAccountTransactionsDetailService(DatabaseInMemoryMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.unit_of_work = SqlUnitOfWork(self.session_factory)
        self.withdraw_command = get_commands(self.unit_of_work)["account_withdraw"]

        with self.unit_of_work as uow:
            account = Account.new()
            account.id = 1
            account.balance = Decimal("500")
            account.person_id = 1
            uow.accounts.add(account)

        self.command = get_commands(self.unit_of_work)["account_transactions"]

    def test_should_return_the_transactions_from_one_second_ago(self):
        self.withdraw_command(1, "100")
        sleep(1)
        self.withdraw_command(1, "100")
        transctions = self.command(1, datetime.utcnow() - timedelta(seconds=1), None)
        self.assertEqual(len(transctions), 1)

    def test_should_return_zero_transactions_when_the_since_parameter_starts_after_the_last_registered_transaction(
        self,
    ):
        self.withdraw_command(1, "100")
        self.withdraw_command(1, "100")
        transctions = self.command(1, datetime.utcnow() + timedelta(seconds=10), None)
        self.assertEqual(len(transctions), 0)

    def test_should_return_zero_transactions_if_the_until_parameter_is_defined_before_the_first_registered_transaction(
        self,
    ):
        self.withdraw_command(1, "100")
        self.withdraw_command(1, "100")
        since = datetime.utcnow() - timedelta(minutes=2)
        until = datetime.utcnow() - timedelta(minutes=1)

        transctions = self.command(1, since, until)
        self.assertEqual(len(transctions), 0)
