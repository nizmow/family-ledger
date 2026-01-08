from datetime import date

from beancount.core import amount, data, number

from scripts.ingest import are_similar


def test_deduplication_logic():
    """Test the are_similar function from ingest.py"""
    meta = data.new_metadata("dummy", 1)
    units = amount.Amount(number.D("100.00"), "USD")
    account = "Assets:Test"

    # Base transaction (like one imported)
    txn1 = data.Transaction(
        meta,
        date(2026, 1, 1),
        "*",
        None,
        "Target Store",
        data.EMPTY_SET,
        data.EMPTY_SET,
        [data.Posting(account, units, None, None, None, None)],
    )

    # Identical transaction
    txn2 = data.Transaction(
        meta,
        date(2026, 1, 1),
        "*",
        None,
        "Target Store",
        data.EMPTY_SET,
        data.EMPTY_SET,
        [data.Posting(account, units, None, None, None, None)],
    )

    assert are_similar(txn1, txn2), "Identical transactions should be similar"

    # Different date
    txn_date = txn1._replace(date=date(2026, 1, 2))
    assert not are_similar(txn1, txn_date), "Different dates should not be similar"

    # Different narration
    txn_desc = txn1._replace(narration="Walmart")
    assert not are_similar(txn1, txn_desc), "Different narration should not be similar"

    # Different amount
    units_diff = amount.Amount(number.D("105.00"), "USD")
    txn_amt = data.Transaction(
        meta,
        date(2026, 1, 1),
        "*",
        None,
        "Target Store",
        data.EMPTY_SET,
        data.EMPTY_SET,
        [data.Posting(account, units_diff, None, None, None, None)],
    )
    assert not are_similar(txn1, txn_amt), "Different amounts should not be similar"

    # Complex case: Existing transaction has multiple split postings, but one matches
    units_neg = amount.Amount(number.D("-100.00"), "USD")
    txn_balanced = data.Transaction(
        meta,
        date(2026, 1, 1),
        "*",
        None,
        "Target Store",
        data.EMPTY_SET,
        data.EMPTY_SET,
        [
            data.Posting(account, units, None, None, None, None),  # Match
            data.Posting(
                "Expenses:General", units_neg, None, None, None, None
            ),  # Split
        ],
    )
    assert are_similar(txn1, txn_balanced), (
        "Should match if at least one posting matches exactly"
    )
