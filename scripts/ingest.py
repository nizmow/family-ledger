import argparse
import os
import sys
from dotenv import load_dotenv

# Ensure root directory is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import beangulp
from beancount import loader
from beancount.core import data
from beancount.parser import printer

import config

# Load environment variables
load_dotenv()


def are_similar(entry1, entry2):
    """Check if two entries are likely duplicates."""
    # Must be same type (Transaction)
    if not isinstance(entry1, data.Transaction) or not isinstance(
        entry2, data.Transaction
    ):
        return False

    # Check date
    if entry1.date != entry2.date:
        return False

    # Check narration (exact match for now, could be fuzzy)
    if entry1.narration != entry2.narration:
        return False

    # Check postings (amounts and accounts)
    match_found = False
    for p1 in entry1.postings:
        for p2 in entry2.postings:
            if p1.units == p2.units and p1.account == p2.account:
                match_found = True
                break
        if match_found:
            break

    return match_found


def main():
    parser = argparse.ArgumentParser(description="Ingest Beancount CSVs")
    parser.add_argument(
        "imports_dir",
        nargs="?",
        default=os.getenv("BEANCOUNT_IMPORTS_DIR", "imports"),
        help="Directory containing CSV files",
    )
    parser.add_argument("--output", default=os.getenv("BEANCOUNT_STAGING_FILE", "staging/import.bean"), help="Output file path")
    parser.add_argument(
        "--ledger", default=os.getenv("BEANCOUNT_MAIN_FILE", "main.bean"), help="Path to main ledger file"
    )

    args = parser.parse_args()

    ingest_dir = args.imports_dir
    ledger_file = args.ledger

    # Resolve paths relative to CWD if necessary, but scripts are usually run from root
    if not os.path.exists(ingest_dir):
        print(f"Error: Import directory '{ingest_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    # Get the importers from config.py
    importers = config.CONFIG

    # Load existing entries for de-duplication
    print(f"; Loading existing entries from {ledger_file}...", file=sys.stderr)
    try:
        existing_entries, errors, options = loader.load_file(ledger_file)
    except Exception as e:
        print(f"Error loading ledger: {e}", file=sys.stderr)
        existing_entries = []

    # Filter existing entries to only Transactions for efficiency
    existing_txns = [e for e in existing_entries if isinstance(e, data.Transaction)]

    # Process files
    entries = []

    # Walk through the directory
    for root, dirs, files in os.walk(ingest_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            filepath = os.path.abspath(filepath)

            # Skip hidden files
            if filename.startswith("."):
                continue

            # Create a cache object for the file (required by beangulp)
            try:
                matched = False
                for importer in importers:
                    file_obj = beangulp.cache.get_file(filepath)

                    if importer.identify(file_obj):
                        print(
                            f"**** Importing {filepath} using {importer.__class__.__name__} ****",
                            file=sys.stderr,
                        )
                        new_entries = importer.extract(file_obj)

                        unique_entries = []
                        for new_entry in new_entries:
                            is_dup = False
                            for existing in existing_txns:
                                if are_similar(new_entry, existing):
                                    is_dup = True
                                    break

                            if not is_dup:
                                unique_entries.append(new_entry)

                        entries.extend(unique_entries)
                        matched = True

                if not matched:
                    print(f"Skipping {filepath} (no importer matched)", file=sys.stderr)

            except Exception as e:
                print(f"Error processing {filepath}: {e}", file=sys.stderr)

    # Output
    if args.output:
        # Ensure directory exists
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w") as f:
            printer.print_entries(entries, file=f)
        print(
            f"Successfully wrote {len(entries)} entries to {args.output}",
            file=sys.stderr,
        )
    else:
        printer.print_entries(entries, file=sys.stdout)


if __name__ == "__main__":
    main()
