import unittest

from banking import exceptions, interfaces
from banking.adapters import SqlUnitOfWork, metadata
from tests import DatabaseInMemoryMixin, create_account


class TestSqlAlchemyTableDeclaration(DatabaseInMemoryMixin, unittest.TestCase):
    def test_should_creates_the_people_table(self):
        self.assertTrue("people" in metadata.tables.keys())

    def test_should_creates_the_transactions_table(self):
        self.assertTrue("transactions" in metadata.tables.keys())

    def test_should_creates_the_accounts_table(self):
        self.assertTrue("accounts" in metadata.tables.keys())


class TestUnitOfWorkUsingSQLSession(DatabaseInMemoryMixin, unittest.TestCase):
    def test_should_be_possivel_add_an_account_and_retrive_it(self):
        account_id = 1

        with SqlUnitOfWork(self.session_factory) as uow:
            account = create_account(account_id)
            uow.accounts.add(account)

        with SqlUnitOfWork(self.session_factory) as uow:
            uow.accounts.fetch(1)

    def test_if_an_exception_occours_the_with_block_should_rollback_the_transation(
        self,
    ):
        """The person_id is a required field, if it is not setted the transaction will
        raise an exception at db level"""

        account_id = 2

        with SqlUnitOfWork(self.session_factory) as uow:
            account = create_account(account_id, person_id=None)
            uow.accounts.add(account)

        with self.assertRaisesRegex(exceptions.DoesNotExist, "Does not exist"):
            with SqlUnitOfWork(self.session_factory) as uow:
                uow.accounts.fetch(1)
