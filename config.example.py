import os
import sys

# Add the current directory to sys.path so we can import modules
sys.path.append(os.path.dirname(__file__))

from importers.commbank import CommBankImporter

# Configure your importers here.
# Pattern: CommBankImporter(account_name, filename_match_pattern)
CONFIG = [
    # CommBankImporter("Assets:Checking", "checking"),
    # CommBankImporter("Assets:Savings", "savings"),
]
