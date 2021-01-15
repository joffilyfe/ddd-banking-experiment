from datetime import date
from decimal import Decimal
from random import randint

from banking.adapters import metadata, sqlalchemy_schema, start_mappers
from banking.domain import Person
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
    behaviors. This mixin set up an global session that is permanant over
    the all tests contained in the test class.

    Keep in your mind: the database is persistente in the
    class test."""

    @classmethod
    def setUpClass(self):
        schema = sqlalchemy_schema(Numeric=SQLiteNumeric)
        engine = create_in_memory_engine()
        start_mappers(**schema)
        self.session_factory = sessionmaker(bind=engine)
        self.session = self.session_factory()

    @classmethod
    def tearDownClass(self):
        metadata.clear()
        clear_mappers()


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
