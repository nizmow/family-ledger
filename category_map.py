import os
import sys
import yaml
import config_utils

# Default to user_rules.yaml if not set
RULES_FILE = config_utils.get_rules_file()

CATEGORY_RULES = {}

def load_rules():
    global CATEGORY_RULES
    if not os.path.exists(RULES_FILE):
        # If no file exists, we just have empty rules, which is fine.
        # We might print a warning to stderr if we were a script, but as a module we stay quiet.
        return

    try:
        with open(RULES_FILE, "r") as f:
            data = yaml.safe_load(f)
            if data and "rules" in data:
                for rule in data["rules"]:
                    pattern = rule.get("pattern")
                    account = rule.get("account")
                    if pattern and account:
                        CATEGORY_RULES[pattern] = account
    except Exception as e:
        print(f"Error loading categorization rules from {RULES_FILE}: {e}", file=sys.stderr)

# Load rules on import
load_rules()
