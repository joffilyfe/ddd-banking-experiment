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
