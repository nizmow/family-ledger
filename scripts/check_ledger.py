import os
import sys
import subprocess

# Ensure root directory is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import config_utils

def main():
    ledger_file = config_utils.get_main_file()
    print(f"Checking {ledger_file}...", file=sys.stderr)

    # We delegate to the standard bean-check command
    result = subprocess.run(["bean-check", ledger_file])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
