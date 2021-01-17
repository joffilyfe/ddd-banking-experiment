from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

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
from banking.domain import TransactionTypeEnum
from banking.services import get_commands


def datetime_last_30_days() -> datetime:
    return datetime.now() - timedelta(days=30)


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


class Detail(BaseModel):
    """Detail message used when some exception occours"""

    detail: str


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


class AccountBalanceSchema(OrmMode):
    """Schema used to shows an account balance"""

    balance: Decimal


class DepositRequestSchema(BaseModel):
    """Schema used to receive a deposit value from body request"""

    value: Decimal


class WithdrawRequestSchema(BaseModel):
    """Schema used to receive a withdraw value from body request"""

    value: Decimal


class AccountTransactionsSchema(OrmMode):
    """Schema used to shows a transaction information"""

    value: Decimal
    type: TransactionTypeEnum
    created_at: datetime


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


@app.get(
    "/accounts/{id}/balance",
    response_model=AccountBalanceSchema,
    responses={
        404: {"model": Detail},
    },
)
def account_balance(id: int, uow=Depends(get_uow_instance)):
    """Retrieves an existing account by id and show its balance"""
    try:
        account = get_commands(uow)["account_fetch"](id)
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail="Account not found")
    else:
        return account


@app.patch(
    "/accounts/{id}/deposit",
    response_model=None,
    responses={
        404: {"model": Detail},
        205: {
            "content": None,
            "description": "The amount was deposited to the account",
        },
    },
    status_code=205,
)
def account_deposit(id: int, data: DepositRequestSchema, uow=Depends(get_uow_instance)):
    """Deposit some amount to the account"""
    try:
        get_commands(uow)["account_deposit"](id, **data.dict())
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail="Account not found")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    else:
        return Response(content=None, status_code=205)


@app.patch(
    "/accounts/{id}/withdraw",
    response_model=None,
    responses={
        404: {"model": Detail},
        205: {"content": None, "description": "The amount was withdrawn from account"},
    },
    status_code=205,
)
def account_withdraw(
    id: int, data: WithdrawRequestSchema, uow=Depends(get_uow_instance)
):
    """Withdraw some amount from an account"""
    try:
        get_commands(uow)["account_withdraw"](id, **data.dict())
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail="Account not found")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    else:
        return Response(content=None, status_code=205)


@app.patch(
    "/accounts/{id}/block",
    response_model=AccountReadSchema,
    responses={
        404: {"model": Detail},
        205: {
            "content": None,
            "description": "Set the status account as 'inactive'",
        },
    },
    status_code=205,
)
def account_block(id: int, uow=Depends(get_uow_instance)):
    """Set the status account as 'inactive'"""
    try:
        account = get_commands(uow)["account_block"](id)
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail="Account not found")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    else:
        return account


@app.get(
    "/accounts/{id}/transactions",
    response_model=List[AccountTransactionsSchema],
    responses={
        404: {"model": Detail},
    },
)
def account_transactions(
    id: int,
    since: Optional[datetime] = datetime_last_30_days(),
    until: Optional[datetime] = None,
    uow=Depends(get_uow_instance),
):
    command = get_commands(uow)["account_transactions"]

    try:
        transactions = command(id, since, until)
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=404, detail="Account not found")
    else:
        return transactions
