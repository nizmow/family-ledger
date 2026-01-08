import io
from datetime import date

import pytest
from beancount.core import amount, data, number

from importers.commbank import CommBankImporter


# Helper to mock file object
class MockFile:
    def __init__(self, name, content):
        self.name = name
        self.content = content


class MockCommBankImporter(CommBankImporter):
    def _open_file(self, file):
        return io.StringIO(file.content)


@pytest.fixture
def dummy_content():
    return "01/01/2026,100.00,Test Deposit,1000.00\n02/01/2026,-50.00,Test Withdrawal,950.00\n"


def test_identify_correct_file(dummy_content):
    importer = MockCommBankImporter("Assets:Test")
    # File name must end in .csv
    file_obj = MockFile("test.csv", dummy_content)
    assert importer.identify(file_obj)


def test_identify_filename_pattern(dummy_content):
    # Matches "checking"
    importer = MockCommBankImporter("Assets:Test", "checking")

    # Should match
    file_match = MockFile("2026_checking.csv", dummy_content)
    assert importer.identify(file_match)

    # Should not match
    file_mismatch = MockFile("2026_savings.csv", dummy_content)
    assert not importer.identify(file_mismatch)


def test_extract_entries(dummy_content):
    importer = MockCommBankImporter("Assets:Test")
    file_obj = MockFile("test.csv", dummy_content)
    entries = importer.extract(file_obj)

    assert len(entries) == 3

    # Check first entry
    entry1 = entries[0]
    assert entry1.date == date(2026, 1, 1)
    assert entry1.narration == "Test Deposit"
    assert entry1.postings[0].units == amount.Amount(number.D("100.00"), "AUD")
    assert entry1.postings[0].account == "Assets:Test"

    # Check second entry
    entry2 = entries[1]
    assert entry2.date == date(2026, 1, 2)
    assert entry2.narration == "Test Withdrawal"
    assert entry2.postings[0].units == amount.Amount(number.D("-50.00"), "AUD")

    # Check balance entry (last)
    entry_bal = entries[2]
    assert isinstance(entry_bal, data.Balance)
    assert entry_bal.date == date(2026, 1, 3)  # Day after last txn
    assert entry_bal.amount == amount.Amount(number.D("950.00"), "AUD")


def test_categorization():
    # Override content to include known/unknown vendors
    content = "01/01/2026,-50.00,Coles Supermarket,950.00\n02/01/2026,-20.00,Unknown Vendor,930.00\n"
    importer = MockCommBankImporter("Assets:Test")
    file_obj = MockFile("test.csv", content)
    entries = importer.extract(file_obj)

    assert len(entries) == 3

    # Known Vendor (Coles)
    entry1 = entries[0]
    assert entry1.flag == "*"
    assert len(entry1.postings) == 2
    assert entry1.postings[1].account == "Expenses:Groceries"

    # Unknown Vendor
    entry2 = entries[1]
    assert entry2.flag == "!"
    assert "review" in entry2.tags
    assert len(entry2.postings) == 2
    assert entry2.postings[1].account == "Expenses:Uncategorized"

    # Balance check
    entry_bal = entries[2]
    assert isinstance(entry_bal, data.Balance)
    assert entry_bal.amount == amount.Amount(number.D("930.00"), "AUD")
