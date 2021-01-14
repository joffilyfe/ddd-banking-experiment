import unittest

from banking.domain import Person


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
