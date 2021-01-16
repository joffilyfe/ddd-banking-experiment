import unittest
from datetime import datetime, timedelta
from random import randint

from banking import exceptions
from banking.domain import Account, Person
from banking.repositories import (
    AccountRepository,
    PersonRepository,
    TransactionRepository,
)
from tests import (
    DatabaseInMemoryMixin,
    create_account,
    create_in_memory_engine,
    create_person,
    create_transaction,
)


class TestPersonRepository(DatabaseInMemoryMixin, unittest.TestCase):
    """Test behavior about PersonRespository. Keep in mind the use of
    DatabaseInMemoryMixin which has session, engine and another things
    in its instance."""

    def setUp(self):
        super().setUp()
        self.repository = PersonRepository(self.session)

    def tearDown(self):
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            self.session.close()

    def test_should_be_possible_to_add_a_person(self):
        person = create_person(id=9000)
        self.repository.add(person)
        self.repository.fetch(person.id)

    def test_should_raise_an_exception_if_person_does_not_exist(self):
        with self.assertRaises(exceptions.DoesNotExist):
            self.repository.fetch(1)


class TestAccountRepository(DatabaseInMemoryMixin, unittest.TestCase):
    def tearDown(self):
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            self.session.close()

    def test_should_be_possible_to_add_an_account_to_the_database(self):
        repository = AccountRepository(self.session)
        account = create_account(account_id=1)
        repository.add(account)
        repository.fetch(1)

    def test_should_raise_an_exception_if_none_account_was_found(self):
        repository = AccountRepository(self.session)

        with self.assertRaisesRegex(exceptions.DoesNotExist, "Does not exist"):
            repository.fetch(2)


class TestTransactionRepository(DatabaseInMemoryMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.repository = TransactionRepository(self.session)
        self.account = create_account(account_id=randint(10, 1000))
        self.session.add(self.account)
        self.session.commit()

    def tearDown(self):
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            self.session.close()

    def test_should_be_possible_to_add_an_transaction_to_the_database(self):
        transaction = create_transaction(id=None)
        self.repository.add(transaction)
        self.session.commit()
        self.repository.fetch(transaction.id)

    def test_should_raise_an_exception_if_none_transaction_was_found(self):
        with self.assertRaisesRegex(exceptions.DoesNotExist, "Does not exist"):
            self.repository.fetch(9999)

    def test_filter_by_interval_should_raise_an_exception_if_the_account_does_not_exist(
        self,
    ):
        with self.assertRaisesRegex(exceptions.DoesNotExist, "Account does not exist"):
            self.repository.filter_by_interval(10000, since=datetime.now())

    def test_filter_by_interval_should_returns_all_transaction_since_a_date(self):
        one_day_before_today = datetime.now() - timedelta(days=1)

        transaction_with_date_before_since = create_transaction(
            id=None,
            account_id=self.account.id,
            created_at=one_day_before_today - timedelta(days=7),
        )
        transaction_today = create_transaction(
            id=None,
            account_id=self.account.id,
            created_at=one_day_before_today,
        )

        self.repository.add(transaction_with_date_before_since)
        self.repository.add(transaction_today)

        self.session.commit()

        transactions = self.repository.filter_by_interval(
            account_id=self.account.id, since=one_day_before_today
        )

        expected = [transaction_today]

        self.assertEqual(transactions, expected)
        self.assertEqual(len(transactions), 1)

    def test_filter_by_interval_should_limit_transactions_by_until_param(self):
        four_days_before = datetime.now() - timedelta(days=4)

        transaction_1 = create_transaction(
            id=None,
            account_id=self.account.id,
            created_at=four_days_before,
        )
        transaction_2 = create_transaction(
            id=None,
            account_id=self.account.id,
            created_at=four_days_before,
        )
        transaction_today = create_transaction(
            id=None,
            account_id=self.account.id,
            created_at=datetime.now(),
        )

        self.repository.add(transaction_1)
        self.repository.add(transaction_2)
        self.repository.add(transaction_today)

        self.session.commit()

        transactions = self.repository.filter_by_interval(
            account_id=self.account.id,
            since=four_days_before,
            until=four_days_before + timedelta(days=2),
        )

        expected = [transaction_1, transaction_2]

        self.assertEqual(transactions, expected)
        self.assertEqual(len(transactions), 2)
