.PHONY: import review accept archive check

import:
	uv run scripts/ingest.py

review:
	uv run scripts/review.py

accept:
	uv run scripts/merge_ledger.py

archive:
	uv run scripts/archive_files.py

check:
	uv run scripts/check_ledger.py
