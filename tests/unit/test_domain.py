import unittest

from banking.domain import Person, Transaction


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
