"""
Copyright (C) 2024 Jath Palasubramaniam
Licensed under the Affero General Public License version 3
"""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import StringConstraints, BaseModel, ConfigDict
from sqlalchemy import String, Integer, Enum as SaEnum, select, delete
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship
import sqlalchemy.exc

from kubera_server.database import OrmBase, get_db, DatabaseError
from kubera_server.logging import get_logger
# from kubera_server import transactions

logger = get_logger()

router = APIRouter(prefix="/accounts", tags=["accounts"])

class AccountTypes(Enum):
    """Allowed account types"""

    EQUITY = "equity"
    ASSET = "asset"
    LIABILITY = "liability"
    REVENUE = "revenue"
    EXPENSE = "expense"

    def __repr__(self):
        return self.value


class AccountSchema(BaseModel):
    """Pydantic model for an account"""

    model_config = ConfigDict(from_attributes = True)

    id: int | None = None
    name: Annotated[str,  StringConstraints(min_length=1)]
    type: AccountTypes

    def __repr__(self):
        return f"Account(id={self.id!r}, name={self.name!r}, type={self.type!r})"

    def __str__(self):
        return repr(self)


class AccountModel(OrmBase):
    """SQLAlchemy model for an account"""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    type: Mapped[AccountTypes] = mapped_column(SaEnum(AccountTypes), nullable=False)

    # debits: Mapped["list[transactions.TransactionModel]"] = relationship(
    #     "transactions.TransactionModel",
    #     foreign_keys=["transactions.TransactionModel.debit"],
    #     back_populates="debit"
    # )
    # credits: Mapped["list[transactions.TransactionModel]"] = relationship(
    #     "transactions.TransactionModel",
    #     foreign_keys=["transactions.TransactionModel.credit"],
    #     back_populates="credit"
    # )


    @classmethod
    def list(cls, db: Session) -> list["AccountModel"]:
        """
        Obtain a list of all accounts within the database
        """

        stmt = select(cls)
        result = db.scalars(stmt).all()

        return result

    @classmethod
    def read(cls, db: Session, account_id: int) -> "AccountModel":
        """
        Read an existing account
        """

        stmt = select(cls).where(cls.id == account_id)
        record = db.scalar(stmt)

        if not record:
            raise DatabaseError(error = "AccountNotFound", message = f"No account with the given id: {account_id}")

        return record

    @classmethod
    def create(cls, db: Session, account: AccountSchema) -> "AccountModel":
        """
        Create a new account
        """

        if account.id is not None:
            raise DatabaseError(message = "ID should be null for new accounts")

        record = cls(**account.model_dump())
        logger.debug("Preparing to insert: %s", repr(record))

        try:
            db.add(record)
            db.commit()
            db.refresh(record)
        except sqlalchemy.exc.IntegrityError as e:
            logger.debug(e)
            raise DatabaseError(message = "Account already exists") from e

        return record

    @classmethod
    def update(cls, db: Session, account: AccountSchema) -> "AccountModel":
        """
        Update an existing account
        """

        if account.id is None:
            raise DatabaseError(message = "ID should not be null for existing accounts")

        stmt = select(cls).where(cls.id == account.id)
        record = db.scalar(stmt)

        if not record:
            raise DatabaseError(message = "Account not found")

        for key, value in account.model_dump().items():
            setattr(record, key, value)

        try:
            db.commit()
        except sqlalchemy.exc.IntegrityError as e:
            if any(s in str(e.orig) for s in [
                "accounts.name", "account_name_not_empty"]):
                raise DatabaseError(message = "Invalid account name") from e

        return record

    @classmethod
    def delete(cls, db: Session, account_id: int) -> None:
        """
        Delete an account (or do nothing if the account doesn't exist)
        """

        # FIXME: Verify there are no transactions against the account before deleting

        stmt = delete(cls).where(cls.id == account_id)
        db.execute(stmt)
        db.commit()

    def __repr__(self):
        return f"Account(id={self.id!r}, name={self.name!r}, type={self.type!r})"


#Duplicate route prevents redirects from trailing slash
@router.get("")
@router.get("/", include_in_schema = False)  # Show only one route in docs
def list_accounts(db: Annotated[Session, Depends(get_db)]) -> list[AccountSchema]:
    """Return a summary list of all accounts"""

    result = AccountModel.list(db)

    return result


@router.get("/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)) -> AccountSchema:
    """Returns details for a single account"""

    logger.debug("get_account()")

    try:
        result = AccountModel.read(db, account_id)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No account with that ID") from e

    return result


# Duplicate route prevents redirects from trailing slash
@router.post("", status_code = status.HTTP_201_CREATED)
@router.post("/", include_in_schema = False, status_code = status.HTTP_201_CREATED)
async def create_account(account: AccountSchema, db: Session = Depends(get_db)) -> AccountSchema:
    """Create a new account"""

    logger.debug("create_account()")
    logger.debug("Received: %s", repr(account))

    try:
        result = AccountModel.create(db, account)
    except DatabaseError as e:
        logger.debug(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Account already exists") from e

    return result


# Duplicate route prevents redirects from trailing slash
@router.put("", status_code = status.HTTP_201_CREATED)
@router.put("/", include_in_schema = False, status_code = status.HTTP_201_CREATED)
def update_account(account: AccountSchema, db: Session = Depends(get_db)) -> AccountSchema:
    """Modify an existing account"""

    logger.debug("update_account()")
    logger.debug("Updating: %s", account)

    try:
        result = AccountModel.update(db, account)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No account with that ID") from e

    return result


@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)) -> None:
    """Delete an existing account"""

    logger.debug("delete_account()")

    AccountModel.delete(db, account_id)
