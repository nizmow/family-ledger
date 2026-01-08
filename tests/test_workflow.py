import os
import sys
from unittest.mock import patch

import pytest

# Import the scripts to test their main execution
from scripts import archive_files, ingest, merge_ledger


def test_merge_ledger(tmp_path):
    # Setup
    staging_file = tmp_path / "staging.bean"
    ledgers_dir = tmp_path / "ledgers"
    ledgers_dir.mkdir()

    # Create staging content
    staging_content = """
2026-01-01 * "Test Transaction"
  Assets:Checking  -10.00 USD
  Expenses:Food     10.00 USD
"""
    staging_file.write_text(staging_content)

    # Run merge_ledger
    with patch.object(
        sys, "argv", ["merge_ledger.py", str(staging_file), str(ledgers_dir)]
    ):
        merge_ledger.main()

    # Verify
    year_file = ledgers_dir / "2026.bean"
    assert year_file.exists()
    assert "Test Transaction" in year_file.read_text()

    # Verify staging is cleared
    assert staging_file.read_text() == ""


def test_archive_files(tmp_path):
    # Setup
    imports_dir = tmp_path / "imports"
    imports_dir.mkdir()
    archive_dir = tmp_path / "archive"

    # Create a dummy CSV that CommBankImporter can identify
    # We need to make sure config.CONFIG is used, so we rely on the real CommBankImporter
    # which checks for .csv extension and 4 columns
    csv_file = imports_dir / "checking.csv"
    csv_content = "01/01/2026,100.00,Test,1000.00\n"
    csv_file.write_text(csv_content)

    # Run archive_files
    with patch.object(
        sys, "argv", ["archive_files.py", str(imports_dir), str(archive_dir)]
    ):
        archive_files.main()

    # Verify
    expected_archive_path = archive_dir / "2026" / "2026-01-01_checking.csv"
    assert expected_archive_path.exists()
    assert not csv_file.exists()


def test_ingest_output(tmp_path):
    # Setup
    imports_dir = tmp_path / "imports"
    imports_dir.mkdir()
    output_file = tmp_path / "output.bean"
    ledger_file = tmp_path / "main.bean"
    ledger_file.write_text('option "title" "Test"')

    # Create dummy CSV
    csv_file = imports_dir / "checking.csv"
    csv_content = "01/01/2026,100.00,Test Deposit,1000.00\n"
    csv_file.write_text(csv_content)

    # Run ingest with --output
    with patch.object(
        sys,
        "argv",
        [
            "ingest.py",
            str(imports_dir),
            "--output",
            str(output_file),
            "--ledger",
            str(ledger_file),
        ],
    ):
        ingest.main()

    # Verify
    assert output_file.exists()
    content = output_file.read_text()
    assert "Test Deposit" in content
    assert "Assets:Joint:Checking" in content
