import argparse
import os
import shutil
import sys

# Ensure root directory is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import beangulp

import config
import config_utils


def main():
    parser = argparse.ArgumentParser(description="Archive imported CSV files")
    parser.add_argument("imports_dir", nargs="?", default=config_utils.get_imports_dir(), help="Directory containing CSV files to archive")
    parser.add_argument("archive_dir", nargs="?", default=config_utils.get_archive_dir(), help="Root directory for archives")

    args = parser.parse_args()

    imports_dir = args.imports_dir
    archive_dir = args.archive_dir

    if not os.path.exists(imports_dir):
        print(f"Error: Imports directory '{imports_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(archive_dir):
        print(f"Creating archive directory '{archive_dir}'...", file=sys.stderr)
        os.makedirs(archive_dir)

    importers = config.CONFIG

    for root, dirs, files in os.walk(imports_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            filepath = os.path.abspath(filepath)

            # Skip hidden files
            if filename.startswith("."):
                continue

            print(f"Processing {filename}...", file=sys.stderr)

            # Identify and extract to find date
            try:
                file_obj = beangulp.cache.get_file(filepath)
                matched_importer = None
                entries = []

                for importer in importers:
                    if importer.identify(file_obj):
                        matched_importer = importer
                        try:
                            entries = importer.extract(file_obj)
                        except Exception as e:
                            print(
                                f"  Warning: Importer matched but failed to extract: {e}",
                                file=sys.stderr,
                            )
                        break

                if matched_importer and entries:
                    # Find earliest date
                    dates = [e.date for e in entries if hasattr(e, "date")]
                    if dates:
                        min_date = min(dates)
                        year = min_date.year
                        date_str = min_date.strftime("%Y-%m-%d")

                        # Construct new path
                        year_dir = os.path.join(archive_dir, str(year))
                        if not os.path.exists(year_dir):
                            os.makedirs(year_dir)

                        new_filename = f"{date_str}_{filename}"
                        dest_path = os.path.join(year_dir, new_filename)

                        # Handle duplicate destination
                        if os.path.exists(dest_path):
                            print(
                                f"  Warning: Destination {dest_path} exists. Appending timestamp.",
                                file=sys.stderr,
                            )
                            import time

                            ts = int(time.time())
                            new_filename = f"{date_str}_{ts}_{filename}"
                            dest_path = os.path.join(year_dir, new_filename)

                        print(f"  Archiving to {dest_path}", file=sys.stderr)
                        shutil.move(filepath, dest_path)
                    else:
                        print(
                            f"  No dates found in entries for {filename}. Moving to 'Unsorted'.",
                            file=sys.stderr,
                        )
                        unsorted_dir = os.path.join(archive_dir, "Unsorted")
                        os.makedirs(unsorted_dir, exist_ok=True)
                        shutil.move(filepath, os.path.join(unsorted_dir, filename))

                elif matched_importer:
                    print(
                        f"  Importer matched but no entries extracted. Skipping.",
                        file=sys.stderr,
                    )
                else:
                    print(f"  No importer matched. Skipping.", file=sys.stderr)

            except Exception as e:
                print(f"  Error processing {filename}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
