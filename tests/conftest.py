"""
Copyright (C) 2024 Jath Palasubramaniam
Licensed under the Affero General Public License version 3
"""

import os
from pathlib import Path

import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

@pytest.fixture()
def test_db(tmp_path):
    """
    Test fixture to provide test database

    Alembic migrations are run to set up the database. The test database will be
    created on disk in a temporary location.
    """

    db_path = tmp_path / "test.db"
    db_uri = f"sqlite:///{db_path}"

    engine = create_engine(db_uri, connect_args={"check_same_thread": False})
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_uri)
    command.upgrade(alembic_cfg, "head")

    with engine.begin() as connection:
        with open(Path("tests", "mock_data.sql"), encoding="utf-8") as file:
            query = text(file.read())
            connection.execute(query)

    try:
        db = session()
        yield db
    finally:
        db.close()
        os.remove(db_path)
