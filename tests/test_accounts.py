"""
Copyright (C) 2024 Jath Palasubramaniam
Licensed under the Affero General Public License version 3
"""

# pylint: disable=missing-function-docstring

import pytest

from kubera_server.accounts import AccountModel, AccountTypes
from kubera_server.database import DatabaseError


def test_list_accounts(test_db):
    result = AccountModel.list(test_db)
    assert isinstance(result, list)
    assert isinstance(result[0], AccountModel)
    assert result[0].id == 1
    assert result[0].name == "Opening Balances"
    assert result[0].type == AccountTypes.EQUITY
    assert len(result) == 10


def test_read_valid_account(test_db):
    result = AccountModel.read(test_db, 2)
    assert isinstance(result, AccountModel)
    assert result.id == 2
    assert result.name == "House"
    assert result.type == AccountTypes.ASSET


def test_read_invalid_account(test_db):
    with pytest.raises(DatabaseError) as e:
        AccountModel.read(test_db, 11)
    assert e.value.error == "AccountNotFound"
