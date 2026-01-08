# Family Ledger

Personal finance tracking using [Beancount](https://beancount.github.io/docs/) and [Fava](https://beancount.github.io/fava/).

This repository contains the automation scripts and structure for managing a double-entry accounting ledger. It is designed to keep your personal data (transactions, account numbers) separate from the code.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd family-ledger
    ```

2.  **Install dependencies:**
    This project uses `uv` for dependency management.
    ```bash
    uv sync
    ```

3.  **Initialize Configuration:**
    Create your local configuration files from the templates.
    ```bash
    cp .env.example .env
    cp config.example.py config.py
    cp accounts.example.bean accounts.bean
    cp main.example.bean main.bean
    cp user_rules.example.yaml user_rules.yaml
    ```

4.  **Customize:**
    *   Edit `.env` if you want to change where data is stored (default is local folders like `ledgers/`, `imports/`).
    *   Edit `accounts.bean` to define your real accounts.
    *   Edit `config.py` to set up your specific account mapping patterns.
    *   Edit `user_rules.yaml` to add regex patterns for auto-categorization (e.g., "Netflix" -> "Expenses:Streaming").

## Workflow

We use a `Makefile` to simplify the standard workflow.

### 1. Capture
Download CSV files from your bank and drop them into the `imports/` folder.
*   **Note:** Filenames matter! The default `CommBankImporter` looks for patterns in the filename (e.g., `checking.csv`, `savings.csv`) to map to the correct Beancount account.

### 2. Import (Staging)
Process the new files and generate a staging file. This step extracts transactions and removes duplicates.

```bash
make import
```
*   **Outcome:** New transactions are written to `staging/import.bean`.

### 3. Review
Launch Fava specifically to review the new, staged transactions.

```bash
make review
```
*   **Action:** Fix descriptions, add tags, or split transactions directly in the Fava UI (by editing the source file) or in your text editor.

### 4. Accept
Merge the reviewed transactions into your permanent ledger.

```bash
make accept
```
*   **Outcome:** Transactions are appended to the correct year file (e.g., `ledgers/2026.bean`), and the staging file is cleared.

### 5. Cleanup
Archive the processed CSV files.

```bash
make archive
```
*   **Outcome:** Source CSVs are renamed (with date prefixes) and moved to `archive/YYYY/`.

## Other Commands

### Validate Ledger
Check your main ledger for syntax errors or imbalances:
```bash
make check
```

### Run Tests
Verify the importer logic (useful if you modify the python scripts):
```bash
uv run pytest
```

## Directory Structure

*   `main.bean`: The entry point for your ledger.
*   `accounts.bean`: Definitions of your Assets, Liabilities, Income, and Expenses.
*   `config.py`: Python configuration for importers.
*   `user_rules.yaml`: Simple regex rules for categorizing transactions.
*   `imports/`: Drop box for new bank CSVs.
*   `staging/`: Workbench for new transactions before they are committed.
*   `ledgers/`: Permanent record, split by year (e.g., `ledgers/2026.bean`).
*   `archive/`: Storage for processed CSV files.
*   `scripts/`: Python logic for the workflow.