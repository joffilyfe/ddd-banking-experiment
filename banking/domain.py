import enum
from decimal import Decimal
from decimal import InvalidOperation as DecimalException

from typing import List

from datetime import datetime, date
from dataclasses import dataclass


@dataclass
class Person:
    """Represents a person in the system"""

    id: int
    name: str
    cpf: str
    born_at: date

    @staticmethod
    def new(id=None, name=None, cpf=None, born_at=None):
        return Person(id=id, name=name, cpf=cpf, born_at=born_at)


class TransactionTypeEnum(str, enum.Enum):
    deposit = "deposit"
    withdraw = "withdraw"


@dataclass
class Transaction:
    """Responsible to hold informations about a account transaction"""

    id: int = None
    account_id: int = None
    value: Decimal = None
    type: TransactionTypeEnum = None
    created_at: datetime = None

    @staticmethod
    def new(id=None, account_id=None, value=None, type=None, created_at=None):
        return Transaction(
            id=id, account_id=account_id, value=value, type=type, created_at=created_at
        )


class Account:
    """Responsible to manage operations over the application"""

    def __init__(
        self,
        id: int,
        balance: Decimal,
        daily_withdrawal_limit: Decimal,
        active: bool,
        type: bool,
        person_id: int,
        transactions: List[Transaction] = None,
    ):
        self.id = id
        self.balance = balance
        self.daily_withdrawal_limit = daily_withdrawal_limit
        self.active = active
        self.type = type
        self.person_id: int = person_id
        self.transactions = [] if transactions is None else transactions

    @staticmethod
    def new():
        return Account(
            id=None,
            balance=Decimal("0.00"),
            daily_withdrawal_limit=Decimal("1000.00"),
            active=True,
            type=1,
            person_id=None,
            transactions=[],
        )

    def unblock(self) -> None:
        """Set the active status as True"""
        self.active = True

    def block(self) -> None:
        """Set the active status as Talse"""
        self.active = False

    def add_transaction(self, t: Transaction) -> None:
        """Adds a transaction to the transactions list"""

        if not isinstance(t, Transaction):
            raise TypeError("Could not add the object '%s' to the transaction list" % t)

        self.transactions.append(t)

    def deposit(self, value: str) -> None:
        """Adds an amout to the account balance.
        It does some minimal validations related to business model like the
        signal of number or if the value interfaces is a number"""

        try:
            _value = Decimal(str(value))
        except (ValueError, DecimalException):
            raise ValueError(
                "Could not deposit the amount '%s' because it isn't"
                " a valid value" % value
            ) from None
        else:
            if _value <= 0:
                raise ValueError(
                    "Could not deposit the value '%s'. "
                    "Only positive values are accepted" % _value
                )
            self.balance = self.balance + _value

    def withdraw(self, value: str) -> None:
        """Withdraw an amount from the account balance.

        It does some minimal validations related to the business model like the
        value interfaces or amount of money withdrawn. Only business model
        validations should be puted here."""

        try:
            _value = Decimal(str(value))
        except (ValueError, DecimalException):
            raise ValueError(
                "Could not withdraw the amount '%s' because it isn't"
                " a valid value" % value
            ) from None

        new_balance = self.balance - _value

        if new_balance < 0:
            raise ValueError(
                "The account balance is insufficient "
                "to withdraw the '%s' ammount" % _value
            ) from None
        elif _value == 0:
            raise ValueError("Could not withdraw an amout of zero from the account")
        elif _value < 0:
            raise ValueError(
                "Could not withdraw the value '%s'. Only positive "
                "values are accepted" % _value
            )
        else:
            self.balance = new_balance
