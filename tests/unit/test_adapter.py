import unittest
from unittest import mock

from banking import exceptions, interfaces
from banking.adapters import SqlUnitOfWork
from banking.domain import Account
from tests.unit import TestingSessionFactory


class TestSessionInstance(unittest.TestCase):
    def setUp(self):
        self.session = TestingSessionFactory({})()

    def test_the_session_should_contains_the_commit_method(self):
        self.assertIsNotNone(self.session.commit)
        self.assertIsNone(self.session.commit())

    def test_session_commit_should_move_data_to_persistent_layer(self):
        account = Account.new()
        account.id = 1
        self.session.add(account)
        self.session.commit()
        self.assertIsNotNone(self.session.query(Account).get(1))

    def test_session_has_rollback_method(self):
        self.assertIsNotNone(self.session.rollback)

    def test_session_has_close_method(self):
        self.assertIsNotNone(self.session.close)


class TestUnitOfWork(unittest.TestCase):
    def setUp(self):
        self.storage = {}
        self.session_factory = TestingSessionFactory(self.storage)
        self.account_1 = Account.new()
        self.account_1.id = 1

    def test_unit_of_work_accounts_method_should_returns_an_repository_entity(self):
        with SqlUnitOfWork(self.session_factory) as u:
            self.assertIsInstance(u.accounts, interfaces.AbstractRepository)

    def test_unit_of_work_transactions_method_should_returns_an_repository_entity(self):
        with SqlUnitOfWork(self.session_factory) as u:
            self.assertIsInstance(u.transactions, interfaces.AbstractRepository)

    def test_unit_of_work_should_commit_automaticaly_when_contextblock_exits(self):
        with SqlUnitOfWork(self.session_factory) as u:
            u.accounts.add(self.account_1)

        with SqlUnitOfWork(self.session_factory) as u:
            self.assertIsInstance(u.accounts.fetch(1), Account)

    def test_unit_of_work_should_rollback_a_transaction_if_an_exception_occurs(self):
        session_factory = TestingSessionFactory(frozenset({}))

        with SqlUnitOfWork(session_factory) as u:
            # will use a frozen set, then the commit should raise
            # an exception and the rollback should be called
            u.accounts.add(self.account_1)

        with self.assertRaises(exceptions.DoesNotExist):
            with SqlUnitOfWork(session_factory) as uow:
                uow.accounts.fetch(1)

    def test_unit_of_work_should_call_the_rollback_method_if_commit_raises_an_exception(
        self,
    ):
        """This test is important during mutation testing. It should guarantee
        a clean session if something goes wrong during the transaction.

        Note: it uses a mock to verify that. Personaly I do not like mocks
        because sometimes if a behavior changes the mock continues with the
        old behavior and the test does not fail."""

        commit_mock = mock.MagicMock(name="commit")
        commit_mock.side_effect = ValueError

        rollback_mock = mock.MagicMock(name="rollback")

        with SqlUnitOfWork(TestingSessionFactory(frozenset({}))) as uow:
            uow.commit = commit_mock
            uow.rollback = rollback_mock
            uow.accounts.add(self.account_1)

        uow.commit.assert_called_once_with()
        uow.rollback.assert_called_once_with()
