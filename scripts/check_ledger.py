import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

def main():
    ledger_file = os.getenv("BEANCOUNT_MAIN_FILE", "main.bean")
    print(f"Checking {ledger_file}...", file=sys.stderr)

    # We delegate to the standard bean-check command
    result = subprocess.run(["bean-check", ledger_file])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
