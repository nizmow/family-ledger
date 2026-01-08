import os
import sys
from unittest.mock import patch

import pytest
from scripts import archive_files, ingest, merge_ledger

# We need to ensure config is loaded.
# Since we are running in the same process, we assume the project's config.py is valid.

def test_full_workflow_via_env_vars(tmp_path):
    """
    Simulates the full "Pull and Go" workflow using environment variables.
    Steps:
    1. Setup directories and env vars.
    2. Create a source CSV.
    3. Run Ingest -> Check staging.
    4. Run Merge -> Check ledger.
    5. Run Archive -> Check archive.
    """

    # 1. Setup
    imports_dir = tmp_path / "imports"
    imports_dir.mkdir()

    staging_file = tmp_path / "staging" / "import.bean"

    ledgers_dir = tmp_path / "ledgers"
    ledgers_dir.mkdir()

    archive_dir = tmp_path / "archive"

    main_file = tmp_path / "main.bean"
    main_file.write_text('option "title" "Test Ledger"\n')

    # Define Env Vars for this test session
    env_vars = {
        "BEANCOUNT_IMPORTS_DIR": str(imports_dir),
        "BEANCOUNT_STAGING_FILE": str(staging_file),
        "BEANCOUNT_LEDGER_DIR": str(ledgers_dir),
        "BEANCOUNT_ARCHIVE_DIR": str(archive_dir),
        "BEANCOUNT_MAIN_FILE": str(main_file),
    }

    with patch.dict(os.environ, env_vars):

        # 2. Create Source CSV
        # We use a filename that matches the default config pattern (checking.csv)
        csv_file = imports_dir / "checking.csv"
        csv_content = "01/01/2026,100.00,Integration Test Transaction,1000.00\n"
        csv_file.write_text(csv_content)

        # 3. Run Ingest
        # We need to patch sys.argv to be empty or minimal, relying on defaults (env vars)
        with patch.object(sys, "argv", ["ingest.py"]):
            ingest.main()

        # Verify Staging
        assert staging_file.exists()
        staging_content = staging_file.read_text()
        assert "Integration Test Transaction" in staging_content
        # Check that it extracted the date correctly (2026-01-01)
        assert "2026-01-01" in staging_content

        # 4. Run Merge (Accept)
        with patch.object(sys, "argv", ["merge_ledger.py"]):
            merge_ledger.main()

        # Verify Ledger
        year_file = ledgers_dir / "2026.bean"
        assert year_file.exists()
        ledger_content = year_file.read_text()
        assert "Integration Test Transaction" in ledger_content

        # Verify Staging is Empty
        assert staging_file.read_text() == ""

        # 5. Run Archive
        with patch.object(sys, "argv", ["archive_files.py"]):
            archive_files.main()

        # Verify Archive
        # It should be in archive/2026/2026-01-01_checking.csv
        expected_archive = archive_dir / "2026" / "2026-01-01_checking.csv"
        assert expected_archive.exists()

        # Verify Source Removed
        assert not csv_file.exists()
