# Archive

One-off plans, reports, and analysis artifacts kept for reference only.
Nothing in this directory is maintained; ruff and pytest exclude it.

- `COMPARISON_PLAN.md`, `COMPARISON_REPORT.md` — aireloom vs aletheca
  comparison (2026-06). The plan's goals were implemented; the report is a
  research result, not documentation.
- `IMPLEMENTATION_PLAN.md`, `VALIDATION_REPORT.md` — the pre-overhaul
  buildout plan for the dacite-era codebase and its validation report. They
  describe code that no longer exists.
- `comprehensive_analysis.py`, `missing_items_analysis.py`,
  `missing_items_report.md` — one-off gap analysis of OpenAlex works fields.
  They needed the `analysis` optional extra, which was removed from
  pyproject.
- `missing_dois.txt`, `missing_items_metadata.json` — about 4 MB of one-off
  research data behind the analysis above.
- `marimo_checks/` — marimo notebook validating dataclass representations
  that no longer exist. Its `__marimo__/` session cache is untracked.
