import csv
import os
import re
from datetime import datetime, timedelta
from typing import TextIO

from beancount.core import amount, data, flags, number
from beangulp import importer

try:
    from category_map import CATEGORY_RULES
except ImportError:
    CATEGORY_RULES = {}


class CommBankImporter(importer.ImporterProtocol):
    def __init__(self, account, filename_pattern=None, currency="AUD"):
        self.account = account
        self.filename_pattern = filename_pattern
        self.currency = currency

    def _open_file(self, file) -> TextIO:
        return open(file.name)

    def identify(self, file):
        # Quick check: extension is .csv
        if not file.name.lower().endswith(".csv"):
            return False

        # Check filename pattern if specified
        if self.filename_pattern:
            # We check against the basename to avoid path issues
            if not re.search(
                self.filename_pattern, os.path.basename(file.name), re.IGNORECASE
            ):
                return False

        try:
            with self._open_file(file) as f:
                reader = csv.reader(f)
                row = next(reader)

                # Check for 4 columns and date format in first column
                if len(row) != 4:
                    return False
                datetime.strptime(row[0], "%d/%m/%Y")
                return True
        except Exception:
            return False

    def extract(self, file, existing_entries=None):
        entries = []
        last_balance = None
        last_date = None
        index = -1

        with self._open_file(file) as f:
            reader = csv.reader(f)
            for index, row in enumerate(reader):
                date_str = row[0]
                amt_str = row[1]
                desc = row[2]

                # Parse date
                date = datetime.strptime(date_str, "%d/%m/%Y").date()

                # Parse amount
                amt = number.D(amt_str)
                units = amount.Amount(amt, self.currency)

                # Categorization
                category = "Expenses:Uncategorized"
                flag = flags.FLAG_WARNING
                tags = frozenset(["review"])

                for pattern, account in CATEGORY_RULES.items():
                    if re.search(pattern, desc, re.IGNORECASE):
                        category = account
                        flag = flags.FLAG_OKAY
                        tags = data.EMPTY_SET
                        break

                meta = data.new_metadata(file.name, index)

                txn = data.Transaction(
                    meta,
                    date,
                    flag,
                    None,
                    desc,
                    tags,
                    data.EMPTY_SET,
                    [
                        data.Posting(self.account, units, None, None, None, None),
                        data.Posting(category, -units, None, None, None, None),
                    ],
                )
                entries.append(txn)

                # Track for balance assertion
                last_balance = number.D(row[3])
                last_date = date

        if entries and last_balance is not None and last_date is not None:
            # Add balance assertion for the day after the last transaction
            # This asserts the balance at the START of the next day
            balance_date = last_date + timedelta(days=1)

            balance_entry = data.Balance(
                data.new_metadata(file.name, index + 1),
                balance_date,
                self.account,
                amount.Amount(last_balance, self.currency),
                None,
                None,
            )
            entries.append(balance_entry)

        # Sort entries by date (and other criteria) to ensure chronological order
        entries.sort(key=data.entry_sortkey)

        return entries
