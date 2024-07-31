"""
Copyright (C) 2024 Jath Palasubramaniam
Licensed under the Affero General Public License version 3
"""

from kubera_server import accounts


def test_list_accounts(test_db):
    result = accounts.AccountModel.list(test_db)
    assert isinstance(result, list)
    assert len(result) == 0