import unittest

from banking.adapters import metadata
from tests import DatabaseInMemoryMixin


class TestSqlAlchemyTableDeclaration(DatabaseInMemoryMixin, unittest.TestCase):
    def test_should_creates_the_people_table(self):
        self.assertTrue("people" in metadata.tables.keys())

    def test_should_creates_the_transactions_table(self):
        self.assertTrue("transactions" in metadata.tables.keys())

    def test_should_creates_the_accounts_table(self):
        self.assertTrue("accounts" in metadata.tables.keys())
