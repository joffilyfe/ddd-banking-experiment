from datetime import date
from dataclasses import dataclass


@dataclass
class Person:
    """Represents a person in the system"""

    id: int
    name: str
    cpf: str
    born_at: date

    @staticmethod
    def new(id=None, name=None, cpf=None, born_at=None):
        return Person(id=id, name=name, cpf=cpf, born_at=born_at)
