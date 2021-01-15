class TestingQueryEngine:
    def __init__(self, data):
        self.data: set = data

    def get(self, id: int):
        for item in self.data:
            if item.id == id:
                return item


class TestingSession:
    """Testing class used to mock expected behavior from a database session"""

    def __init__(self, storage):
        self.temporary_storage = {}
        self.storage = storage

    def query(self, key):
        return TestingQueryEngine(dict(self.storage).get(key, set()))

    def add(self, entity):
        self.temporary_storage.setdefault(entity.__class__, set())
        self.temporary_storage[entity.__class__].add(entity)

    def commit(self):
        """When a commit is trigged the 'database' will move
        the temporary data to permanent area"""

        for key, items in self.temporary_storage.items():
            self.storage.setdefault(key, set())

            for item in items:
                self.storage[key].add(item)

        self.temporary_storage = {}

    def rollback(self):
        self.temporary_storage = {}

    def close(self):
        pass


class TestingSessionFactory:
    """Creates a session factory objecto to be used during an transaction"""

    def __init__(self, storage):
        self.storage = storage

    def __call__(self):
        return TestingSession(self.storage)
