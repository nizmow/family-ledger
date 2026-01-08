import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

def main():
    # Gather paths from env
    staging_file = os.getenv("BEANCOUNT_STAGING_FILE", "staging/import.bean")
    accounts_file = os.getenv("BEANCOUNT_ACCOUNTS_FILE", "accounts.bean")

    # We need to construct a review file that includes the accounts and the staging file.
    # The review file should ideally be in the same dir as staging file to resolve relative imports if needed,
    # OR we use absolute paths in the include.

    # Let's create a temporary review file
    review_file = "staging/review.bean" # Default location

    # Ensure staging dir exists
    os.makedirs(os.path.dirname(review_file), exist_ok=True)

    # Convert to absolute paths to avoid relative include hell
    abs_accounts = os.path.abspath(accounts_file)
    abs_staging = os.path.abspath(staging_file)

    content = f"""
option "title" "Staging Review"
option "operating_currency" "AUD"

include "{abs_accounts}"
include "{abs_staging}"
"""

    with open(review_file, "w") as f:
        f.write(content)

    print(f"Generated review configuration at {review_file}", file=sys.stderr)
    print(f"Starting Fava...", file=sys.stderr)

    # Run fava
    try:
        subprocess.run(["fava", review_file])
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
