import argparse
import os
import sys
from collections import defaultdict

# Ensure root directory is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import config_utils
from beancount import loader
from beancount.core import data
from beancount.parser import printer


def main():
    parser = argparse.ArgumentParser(
        description="Merge staged transactions into ledger"
    )
    parser.add_argument("staging_file", nargs="?", default=config_utils.get_staging_file(), help="Path to the staging bean file")
    parser.add_argument("ledgers_dir", nargs="?", default=config_utils.get_ledger_dir(), help="Directory containing yearly ledger files")

    args = parser.parse_args()

    staging_file = args.staging_file
    ledgers_dir = args.ledgers_dir

    if not os.path.exists(staging_file):
        print(f"Error: Staging file '{staging_file}' not found.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(ledgers_dir):
        print(f"Error: Ledgers directory '{ledgers_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    # Load the staging file
    print(f"Loading entries from {staging_file}...", file=sys.stderr)
    try:
        entries, errors, options = loader.load_file(staging_file)
    except Exception as e:
        print(f"Error loading staging file: {e}", file=sys.stderr)
        sys.exit(1)

    if not entries:
        print("No entries found in staging file.", file=sys.stderr)
        sys.exit(0)

    # Group entries by year
    entries_by_year = defaultdict(list)
    for entry in entries:
        if hasattr(entry, "date"):
            entries_by_year[entry.date.year].append(entry)
        else:
            # Directives without date (unlikely in this workflow but possible)
            # Default to current year or handle specific logic
            print(f"Warning: Entry without date found: {entry}", file=sys.stderr)

    # Append to year files
    for year, year_entries in entries_by_year.items():
        ledger_path = os.path.join(ledgers_dir, f"{year}.bean")

        # Ensure file exists
        if not os.path.exists(ledger_path):
            print(f"Creating new ledger file: {ledger_path}", file=sys.stderr)
            with open(ledger_path, "w") as f:
                f.write(f"; Transactions for {year}\n\n")

        print(
            f"Appending {len(year_entries)} entries to {ledger_path}...",
            file=sys.stderr,
        )

        # Sort entries by date before writing?
        # Usually it's better to sort, but appending implies chronological order if import was chronological.
        # Beancount doesn't strictly require sorted file, but it's nice.
        # We'll just append for now to be safe and simple.

        with open(ledger_path, "a") as f:
            printer.print_entries(year_entries, file=f)

    # Clear staging file
    print(f"Clearing {staging_file}...", file=sys.stderr)
    with open(staging_file, "w") as f:
        f.write("")  # Empty file

    print("Merge complete.", file=sys.stderr)


if __name__ == "__main__":
    main()
