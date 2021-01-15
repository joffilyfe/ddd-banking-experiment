import logging
from datetime import date, datetime

from mutpy.utils import notmutate
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Enum,
)
from sqlalchemy.orm import mapper, relationship, sessionmaker

from banking import domain, interfaces, repositories
from banking.domain import TransactionTypeEnum

LOGGER = logging.getLogger(__name__)
metadata = MetaData()


@notmutate
def sqlalchemy_schema(Numeric=Numeric):
    people = Table(
        "people",
        metadata,
        Column("idPessoa", Integer, key="id", primary_key=True, autoincrement=True),
        Column("nome", String(255), key="name", nullable=False),
        Column("cpf", String(14), key="cpf", nullable=False),
        Column(
            "dataNascimento",
            Date,
            key="born_at",
            nullable=False,
            default=date.today,
        ),
    )

    transactions = Table(
        "transactions",
        metadata,
        Column("idTransacao", Integer, key="id", primary_key=True, autoincrement=True),
        Column("idConta", ForeignKey("accounts.id"), key="account_id", nullable=False),
        Column("valor", Numeric(10, 2), key="value", nullable=False),
        Column(
            "tipo",
            Enum(
                TransactionTypeEnum,
                values_callable=lambda enum: [e.value for e in enum],
            ),
            key="type",
            nullable=False,
        ),
        Column(
            "dataCriacao",
            DateTime,
            key="created_at",
            nullable=False,
            default=datetime.utcnow,
        ),
    )

    accounts = Table(
        "accounts",
        metadata,
        Column("idConta", Integer, key="id", primary_key=True, autoincrement=True),
        Column("idPessoa", ForeignKey("people.id"), key="person_id", nullable=False),
        Column("saldo", Numeric(10, 2), key="balance", nullable=False),
        Column(
            "limiteSaqueDiario",
            Numeric(10, 2),
            key="daily_withdrawal_limit",
            nullable=False,
        ),
        Column("flagAtivo", Boolean, key="active", nullable=False, default=True),
        Column("tipoConta", Integer, key="type", nullable=False, default=1),
        Column(
            "dataCriacao",
            DateTime,
            key="created_at",
            nullable=False,
            default=datetime.utcnow,
        ),
    )

    return {"people": people, "transactions": transactions, "accounts": accounts}


@notmutate
def start_mappers(people, accounts, transactions):
    """It starts the mapper between sqlalchemy and the domain classes"""

    LOGGER.debug("Starting mappers")

    people_mapper = mapper(
        domain.Person,
        people,
        properties={
            "accounts": relationship(domain.Account, back_populates="person"),
        },
    )
    accounts_mapper = mapper(
        domain.Account,
        accounts,
        properties={
            "transactions": relationship(domain.Transaction, back_populates="account"),
            "person": relationship(people_mapper, back_populates="accounts"),
        },
    )

    mapper(
        domain.Transaction,
        transactions,
        properties={
            "account": relationship(accounts_mapper, back_populates="transactions")
        },
    )


class SqlSessionFactory:
    """Creates a session factory object to be used during an transaction"""

    def __init__(self, engine):
        self.engine = engine

    def __call__(self):
        return sessionmaker(bind=self.engine)()


class SqlUnitOfWork(interfaces.AbstractUnitOfWork):
    """Represents a unit of work used during the interaction with database"""

    @notmutate
    def __init__(self, session_factory: SqlSessionFactory):
        self.session_factory = session_factory

    @notmutate
    def __enter__(self):
        self.session = self.session_factory()
        return super().__enter__()

    def __exit__(self, exc_type, exc, exc_tb) -> None:

        if exc_type:
            self.rollback()
            self.session.close()  # pylint: disable=no-member
            LOGGER.exception(
                "Some exception was raised during __exit__ invocation."
                " Rolling back the transaction."
            )
        else:
            try:
                self.commit()
            except Exception:
                self.rollback()
                self.session.close()  # pylint: disable=no-member
                LOGGER.exception(
                    "Some exception was raised during commit()"
                    " Rolling back the transaction."
                )

    def rollback(self):
        self.session.rollback()  # pylint: disable=no-member

    def commit(self):
        self.session.commit()  # pylint: disable=no-member

    @property
    def accounts(self) -> repositories.AccountRepository:
        return repositories.AccountRepository(self.session)

    @property
    def transactions(self) -> repositories.TransactionRepository:
        return repositories.TransactionRepository(self.session)

    @property
    def people(self) -> repositories.PersonRepository:
        return repositories.PersonRepository(self.session)