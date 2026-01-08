import os
import sys

# Ensure root directory is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import config_utils

def check_path(name, path, is_dir=False, must_exist=True):
    if not path:
        print(f"❌ {name} is not set.", file=sys.stderr)
        return False

    if must_exist:
        if not os.path.exists(path):
            print(f"❌ {name}: Path '{path}' does not exist.", file=sys.stderr)
            return False

        if is_dir and not os.path.isdir(path):
             print(f"❌ {name}: '{path}' is not a directory.", file=sys.stderr)
             return False
        if not is_dir and not os.path.isfile(path):
             print(f"❌ {name}: '{path}' is not a file.", file=sys.stderr)
             return False

    print(f"✅ {name}: {path}")
    return True

def main():
    print("Verifying environment configuration...\n")
    success = True

    # Check Files
    if not check_path("Main Ledger", config_utils.get_main_file()): success = False
    if not check_path("Accounts File", config_utils.get_accounts_file()): success = False
    if not check_path("Rules File", config_utils.get_rules_file()): success = False

    # Check Directories
    if not check_path("Imports Dir", config_utils.get_imports_dir(), is_dir=True): success = False
    if not check_path("Ledgers Dir", config_utils.get_ledger_dir(), is_dir=True): success = False
    if not check_path("Archive Dir", config_utils.get_archive_dir(), is_dir=True): success = False

    # Check Staging Directory
    staging_path = config_utils.get_staging_file()
    if staging_path:
        staging_dir = os.path.dirname(staging_path)
        if not os.path.exists(staging_dir):
             print(f"❌ Staging Dir: Directory '{staging_dir}' does not exist.", file=sys.stderr)
             success = False
        else:
             print(f"✅ Staging Dir: {staging_dir}")

    print("\n" + ("Configuration OK! 🎉" if success else "Configuration has errors. ⚠️"))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
