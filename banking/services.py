from decimal import Decimal

from banking import domain
from banking.repositories import AccountRepository
from banking.interfaces import AbstractUnitOfWork


class Command:
    """Implements the basic command class that should be
    extended by Commands Services"""

    def __init__(self, UnitOfWork):
        self.UnitOfWork = UnitOfWork


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


def get_commands(uow: AbstractUnitOfWork) -> dict:
    return {
        "account_register": AccountRegisterCommand(uow),
        "account_deposit": AccountDepositValueCommand(uow),
    }
