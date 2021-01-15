import unittest
from decimal import Decimal

from banking.domain import Person, Transaction, Account


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


class TestAccountDomain(unittest.TestCase):
    def setUp(self):
        self.account = Account.new()

    def test_should_create_a_default_instance(self):
        self.assertIsNone(self.account.id)
        self.assertEqual(Decimal("0"), self.account.balance)
        self.assertEqual(Decimal("1000"), self.account.daily_withdrawal_limit)
        self.assertEqual(1, self.account.type)
        self.assertEqual(True, self.account.active)
        self.assertEqual([], self.account.transactions)
        self.assertEqual(None, self.account.person_id)

    def test_the_method_new_should_be_static(self):
        self.assertEqual(type(Account.__dict__["new"]), staticmethod)

    def test_should_be_possible_to_deactivate_the_account(self):
        self.assertTrue(self.account.active)
        self.account.block()
        self.assertFalse(self.account.active)

    def test_should_be_possible_to_reactivate_the_account(self):
        self.assertTrue(self.account.active)
        self.account.block()
        self.assertFalse(self.account.active)
        self.account.unblock()
        self.assertTrue(self.account.active)

    def test_should_be_possible_to_deposit_a_value(self):
        self.account.deposit("10.00")
        self.assertEqual(Decimal("10.00"), self.account.balance)

    def test_should_be_possible_to_deposit_cents_to_account(self):
        self.account.deposit("0.15")

    def test_should_raise_a_exception_if_the_deposit_value_is_lower_or_equal_to_zero(
        self,
    ):
        with self.assertRaisesRegex(
            ValueError,
            "Could not deposit the value '-1'. Only positive values are accepted",
        ):
            self.account.deposit(-1)

        with self.assertRaisesRegex(
            ValueError,
            "Could not deposit the value '0'. Only positive values are accepted",
        ):
            self.account.deposit(0)

    def test_should_not_be_possible_to_deposit_a_non_numerical_value(self):
        with self.assertRaisesRegex(
            ValueError,
            "^Could not deposit the amount '@' because it isn't a valid value$",
        ):
            self.account.deposit("@")

    def test_should_be_possible_to_withdraw_a_value(self):
        self.account.deposit("10.00")
        self.account.withdraw("8")
        self.assertEqual(Decimal("2.00"), self.account.balance)

    def test_should_not_be_possible_to_withdraw_a_negative_value(self):
        self.account.deposit("10.00")

        with self.assertRaisesRegex(
            ValueError,
            "^Could not withdraw the value '-8'. Only positive values are accepted$",
        ):
            self.account.withdraw("-8")

        self.assertEqual(self.account.balance, 10)

    def test_should_not_be_possible_to_withdraw_a_non_numerical_value(self):
        with self.assertRaisesRegex(ValueError, "^Could not withdraw"):
            self.account.withdraw("#")

    def test_should_raise_an_exception_if_the_withdraw_amount_is_bigger_then_the_balance(
        self,
    ):
        with self.assertRaisesRegex(
            ValueError,
            "^The account balance is insufficient to withdraw the '100.00' ammount$",
        ):
            self.account.withdraw("100.00")

    def test_should_raise_a_exception_if_the_withdraw_amount_is_zero(self):
        with self.assertRaisesRegex(
            ValueError, "Could not withdraw an amout of zero from the account"
        ):
            self.account.withdraw("0")
