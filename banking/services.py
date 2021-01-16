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


def get_commands(uow: AbstractUnitOfWork) -> dict:
    return {
        "account_register": AccountRegisterCommand(uow),
    }
