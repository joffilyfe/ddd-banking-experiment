import unittest
from random import randint
from decimal import Decimal

from banking import exceptions
from banking.adapters import SqlUnitOfWork
from banking.domain import Account
from banking.services import get_commands
from tests import DatabaseInMemoryMixin, create_person


class TestAccountCreateService(DatabaseInMemoryMixin, unittest.TestCase):
    def setUp(self):
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
