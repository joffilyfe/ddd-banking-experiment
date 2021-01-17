from datetime import datetime
from decimal import Decimal

from banking import domain
from banking.repositories import AccountRepository
from banking.interfaces import AbstractUnitOfWork


class Command:
    """Implements the basic command class that should be
    extended by Commands Services"""

    def __init__(self, UnitOfWork):
        self.UnitOfWork = UnitOfWork


class PersonRegisterCommand(Command):
    """Register a person"""

    def __call__(self, name, cpf, born_at):
        with self.UnitOfWork as uow:
            person = domain.Person.new(
                name=name,
                cpf=cpf,
                born_at=born_at,
            )
            uow.people.add(person)

        return person


class AccountRegisterCommand(Command):
    """Register an user"""

    def __call__(self, person_id, type_id):
        with self.UnitOfWork as uow:
            person = uow.people.fetch(person_id)
            account = domain.Account.new()
            account.type = type_id
            account.person_id = person_id
            uow.accounts.add(account)

        return account


class AccountDepositValueCommand(Command):
    """Obtain an account using the account id then deposit
    a value to the account"""

    def __call__(self, id: int, value: Decimal):
        with self.UnitOfWork as uow:
            account = uow.accounts.fetch(id)
            account.deposit(value)
            account.add_transaction(
                domain.Transaction.new(
                    value=value,
                    type=domain.TransactionTypeEnum.deposit,
                )
            )

        return account


class AccountFetchCommand(Command):
    """Obtain an account using the account id"""

    def __call__(self, id: int):
        with self.UnitOfWork as uow:
            account = uow.accounts.fetch(id)

        return account


class AccountWithddrawValueCommand(Command):
    """Obtain an account using the account id then withdraw
    a value from the account"""

    def __call__(self, id: int, value: Decimal):
        with self.UnitOfWork as uow:
            account = uow.accounts.fetch(id)
            account.withdraw(value)
            account.add_transaction(
                domain.Transaction.new(
                    value=value,
                    type=domain.TransactionTypeEnum.withdraw,
                )
            )

        return account


class AccountBlockCommand(Command):
    """Fetch an account and sets it as blocked"""

    def __call__(self, id: int):
        with self.UnitOfWork as uow:
            account = uow.accounts.fetch(id)
            account.block()
            uow.accounts.add(account)

        return account


class AccountTransactionsDetailCommand(Command):
    """Retrieves the account transaction details by date interval"""

    def __call__(self, account_id: int, since: datetime, until: datetime):
        with self.UnitOfWork as uow:
            transactions = uow.transactions.filter_by_interval(
                account_id=account_id, since=since, until=until
            )

        return transactions


def get_commands(uow: AbstractUnitOfWork) -> dict:
    return {
        "person_register": PersonRegisterCommand(uow),
        "account_register": AccountRegisterCommand(uow),
        "account_deposit": AccountDepositValueCommand(uow),
        "account_fetch": AccountFetchCommand(uow),
        "account_withdraw": AccountWithddrawValueCommand(uow),
        "account_block": AccountBlockCommand(uow),
        "account_transactions": AccountTransactionsDetailCommand(uow),
    }
