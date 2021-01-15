import abc


class AbstractRepository(abc.ABC):
    """Defines the fundamental method that should be implemented by
    repository concrete class."""

    @abc.abstractmethod
    def fetch(self, id):
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, entity):
        raise NotImplementedError


class AbstractUnitOfWork(abc.ABC):
    """Defines the basic interface to the unit of work classes.

    The concrete class must know how the methods should work."""

    def __enter__(self):
        return self

    @abc.abstractmethod
    def __exit__(self, exc_type, exc, exc_tb) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def accounts(self) -> AbstractRepository:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def transactions(self) -> AbstractRepository:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def people(self) -> AbstractRepository:
        raise NotImplementedError