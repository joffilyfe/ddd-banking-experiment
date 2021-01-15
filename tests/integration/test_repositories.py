import unittest

from banking import exceptions
from banking.domain import Person
from banking.repositories import PersonRepository
from tests import (
    DatabaseInMemoryMixin,
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


