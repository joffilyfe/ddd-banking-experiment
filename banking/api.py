from datetime import datetime
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, Response
from pydantic import BaseModel, BaseSettings  # pylint: disable=no-name-in-module
from sqlalchemy import create_engine

from banking import exceptions
from banking.adapters import (
    SqlSessionFactory,
    SqlUnitOfWork,
    metadata,
    sqlalchemy_schema,
    start_mappers,
)
from banking.services import get_commands


class Settings(BaseSettings):
    """Reads the settings file in the root directory.

    It gives preference for environment variables of course."""

    sqlalchemy_database_url: str

    class Config:
        """Read file"""

        env_file = ".env"


# loads application settings
settings = Settings()

# instantiate the application var
app = FastAPI()

# Builds the engine used to open database connections
engine = create_engine(
    name_or_url=settings.sqlalchemy_database_url,
)


@app.on_event("startup")
async def startup_event():
    """Starts the database schema when applications is booted"""

    schema = sqlalchemy_schema()
    start_mappers(**schema)
    metadata.create_all(engine)


# Yields the UnitOfWork used to do the job
# This pattern is strange but its the way that
# FastAPI does.
# Maybe it could be modified to an middleware or something
# like that.
def get_uow_instance():
    """Yield a UnitOfWork used to do database operations.

    Here we made a glue between API layer and adapter layer."""

    session_factory = SqlSessionFactory(engine)
    unit = SqlUnitOfWork(session_factory)

    try:
        yield unit
    finally:
        pass


class OrmMode(BaseModel):
    """A base model used to extend the ORM mode"""

    class Config:
        orm_mode = True


class AccountReadSchema(OrmMode):
    """Schema used to shows an account public information"""

    id: int
    daily_withdrawal_limit: Decimal
    active: bool
    created_at: datetime


class AccountCreateSchema(BaseModel):
    """Schema used to create an account"""

    person_id: int
    type_id: int


@app.post(
    "/accounts",
    response_model=AccountReadSchema,
    responses={
        201: {
            "content": None,
            "description": "Account created successfully",
        },
    },
    status_code=201,
)
def account_register(user: AccountCreateSchema, uow=Depends(get_uow_instance)):
    """Register an account"""
    try:
        account = get_commands(uow)["account_register"](**user.dict())
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail="Person not found")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    else:
        return account
