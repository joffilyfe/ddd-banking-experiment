from decimal import Decimal

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


@dataclass
class Transaction:
    """Responsible to hold informations about a account transaction"""

    id: int = None
    account_id: int = None
    value: Decimal = None
    created_at: datetime = None

    @staticmethod
    def new(id=None, account_id=None, value=None, created_at=None):
        return Transaction(
            id=id, account_id=account_id, value=value, created_at=created_at
        )
