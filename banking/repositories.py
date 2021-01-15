from datetime import datetime
from typing import List

from banking import domain, exceptions, interfaces


class BaseRepository(interfaces.AbstractRepository):
    """Defines the basic operations to all entity repositories.

    It does not implements the DomainClass which must be defined by
    all class that extends this base."""

    def __init__(self, session):
        self._session = session

    def fetch(self, id: int):
        entity = self._session.query(self.DomainClass).get(id)

        if entity is None:
            raise exceptions.DoesNotExist("Does not exist")

        return entity

    def add(self, entity) -> None:
        self._session.add(entity)


class PersonRepository(BaseRepository):
    DomainClass = domain.Person


class AccountRepository(BaseRepository):
    DomainClass = domain.Account


class TransactionRepository(BaseRepository):
    DomainClass = domain.Transaction

    def filter_by_interval(
        self, account_id: int, since: datetime, until: datetime = None
    ) -> List[domain.Transaction]:
        """Retrieves  a list of transactions based in account id and in
        the date interval.

        The `since` parameter is required but the `until` is not. It
        means that result will return all transactions since a start
        date if the until is not passed"""

        if self._session.query(domain.Account).get(account_id) is None:
            raise exceptions.DoesNotExist("Account does not exist")

        filters = [
            domain.Transaction.account_id == account_id,
            domain.Transaction.created_at >= since,
        ]

        if until is not None:
            filters.append(domain.Transaction.created_at <= until)

        return self._session.query(domain.Transaction).filter(*filters).all()
