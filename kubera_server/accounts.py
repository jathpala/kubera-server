"""
Copyright (C) 2024 Jath Palasubramaniam
Licensed under the Affero General Public License version 3
"""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import StringConstraints, BaseModel, ConfigDict
from sqlalchemy import String, Integer, Enum as SaEnum, select
from sqlalchemy.orm import Session, Mapped, mapped_column

from kubera_server.database import OrmBase, get_db
from kubera_server.logging import get_logger

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

    @classmethod
    def list(cls, db: Session) -> list["AccountModel"]:
        """
        Obtain a list of all accounts within the database
        """

        stmt = select(cls)
        result = db.scalars((stmt)).all()

        return result


#Duplicate route prevents redirects from trailing slash
@router.get("")
@router.get("/", include_in_schema = False)  # Show only one route in docs
def list_accounts(db: Annotated[Session, Depends(get_db)]) -> list[AccountSchema]:
    """Return a summary list of all accounts"""

    result = AccountModel.list(db)

    return result
