import os
import sys

# Ensure the root directory is in sys.path so we can import category_map
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from beancount import loader
from beancount.core import data

from category_map import CATEGORY_RULES


def test_category_map_accounts_exist_in_ledger():
    """
    Ensure that every account defined in category_map.py exists as an open account in the ledger.
    """
    # Assuming the test is run from the project root or we can find main.bean relative to here
    # The simplest is to rely on pytest running from root, or construct path
    ledger_file = os.path.join(os.path.dirname(__file__), "..", "main.bean")
    ledger_file = os.path.abspath(ledger_file)

    # Ensure ledger file exists
    assert os.path.exists(ledger_file), f"{ledger_file} not found"

    entries, errors, options = loader.load_file(ledger_file)

    # Filter for Open directives
    open_accounts = {e.account for e in entries if isinstance(e, data.Open)}

    mapped_accounts = set(CATEGORY_RULES.values())

    missing_accounts = mapped_accounts - open_accounts

    assert not missing_accounts, (
        f"The following accounts from category_map.py are missing in {ledger_file}: {missing_accounts}"
    )
