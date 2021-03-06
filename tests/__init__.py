from datetime import date
from decimal import Decimal
from random import randint

from banking.adapters import metadata, sqlalchemy_schema, start_mappers
from banking.domain import Account, Person, Transaction, TransactionTypeEnum
from sqlalchemy import TypeDecorator, Integer, create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker


class SQLiteNumeric(TypeDecorator):
    """Helper class to handle the decimal number in the SQLite database.

    It will translate the decimal to an Integer notation and translate back
    to Decimal type in Python."""

    impl = Integer

    def __init__(self, base, scale):
        TypeDecorator.__init__(self)
        self.scale = scale
        self.multiplier_int = base ** self.scale

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = int(Decimal(value) * self.multiplier_int)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = Decimal(value) / self.multiplier_int
        return value


class DatabaseInMemoryMixin:
    """Provides the basic infrastructure to test the database dependent
    behaviors. This mixin set local session that is volatile and will be
    purged after another test starts.

    Its necessary to call the super().setUp() if you override the setUp
    method."""

    def setUp(self):
        metadata.clear()
        clear_mappers()
        self.schema = sqlalchemy_schema(Numeric=SQLiteNumeric)
        self.engine = create_in_memory_engine()
        start_mappers(**self.schema)
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = self.session_factory()


def create_in_memory_engine():
    """Creates an in memory database using sqlite"""

    engine = create_engine("sqlite:///")
    metadata.create_all(engine)
    return engine


def create_person(id=randint(1, 2000)):
    cpf = (
        randint(100, 200),
        randint(200, 300),
        randint(300, 400),
        randint(10, 99),
    )

    person = Person.new(
        id=id,
        name="Testing",
        cpf="%s.%s.%s-%s" % cpf,
        born_at=date.today(),
    )

    return person


def create_account(account_id=randint(1, 2000), person_id=randint(1, 20000)):
    account = Account.new()
    account.id = account_id
    account.person_id = person_id
    return account


def create_transaction(
    id=randint(1, 2000),
    account_id=randint(1, 2000),
    value=randint(1, 2000),
    type=TransactionTypeEnum.withdraw,
    created_at=None,
):
    return Transaction.new(
        id=id, account_id=account_id, value=value, type=type, created_at=created_at
    )
