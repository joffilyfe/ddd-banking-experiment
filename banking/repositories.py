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
