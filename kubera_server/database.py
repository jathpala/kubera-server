"""
Copyright (C) 2024 Jath Palasubramaniam
Licensed under the Affero General Public License version 3
"""
# pylint: disable=too-few-public-methods

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from kubera_server.config import get_settings
from kubera_server.logging import get_logger

logger = get_logger()

settings = get_settings()

DB_URI = f"sqlite:///{settings.db_path}"
logger.debug("Using database: %s", DB_URI)

engine = create_engine(DB_URI, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class OrmBase(DeclarativeBase):
    """Base class for ORM models"""

def get_db():
    """Return a database connection"""

    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
