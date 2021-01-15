import unittest

from banking import exceptions
from banking.domain import Account, Person
from banking.repositories import AccountRepository, PersonRepository
from tests import (
    DatabaseInMemoryMixin,
    create_account,
    create_in_memory_engine,
    create_person,
)


class TestPersonRepository(DatabaseInMemoryMixin, unittest.TestCase):
    """Test behavior about PersonRespository. Keep in mind the use of
    DatabaseInMemoryMixin which has session, engine and another things
    in its instance."""

    def setUp(self):
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
