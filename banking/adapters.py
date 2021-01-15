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
    TypeDecorator,
)
from sqlalchemy.orm import mapper, relationship, sessionmaker

from banking import domain, interfaces, repositories

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
