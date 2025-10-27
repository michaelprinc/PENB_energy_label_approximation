# GitHub Copilot • Code Review & Hardening Instructions (PRs)

Scope
- Used by Copilot **only** for pull request reviews and hardening guidance.
- Priorities: correctness > security > maintainability > performance > style.

Pre-flight
- Summarize PR intent and risk (low/med/high).
- Identify affected APIs, configs, migrations, and scripts.

Definition of Done (Review)
- All checks green; actionable, anchored comments; minimal diffs for fixes.
- If blocking issues → REQUEST CHANGES with concrete patches.

Automated Checks (Python examples)
- Style: `flake8` (PEP8); report violations as `file:line:code:msg`.
- Formatting: `black --check .` (suggest command if failing).
- Imports: `isort --check-only .` (or `ruff check --select I`).
- Types (if configured): `mypy`/`pyright` on changed files.
- Tests: `pytest -q` on impacted paths; note coverage if available.
- Security: flag secrets/keys in diff; suggest env/secret store. If deps changed, run `pip-audit`/`safety`.

Style/PEP8
- Enforce via flake8; allow `# noqa:<code>` only with justification.
- Public APIs need docstrings (summary + args/returns/raises).
- Clear naming; intent-focused comments; document invariants.

Correctness & Design
- Validate contracts, edge cases, error handling; prefer pure functions.
- Avoid hidden state; ensure async/thread safety if relevant.
- IO/DB/migrations: transactional; backup + rollback plan; no destructive ops without explicit confirmation.

Performance
- Watch complexity in hot paths; avoid N+1 queries; note memory hotspots.

Security & Privacy
- No hardcoded secrets; parametrize credentials; least privilege.
- Validate inputs; encode outputs; avoid injection and unsafe eval/exec.

Change Management
- Smallest viable patch; stable public surface; update README/CHANGELOG/examples.

Review Output (format)
REVIEW SUMMARY:
- Verdict: PASS / REQUEST CHANGES
- Risk: <low|med|high> — why

FINDINGS:
1) [file.py:L123] (Severity: High) <issue>
   Suggestion (patch):
   ```diff
   - ...
   + ...
   ```

CHECKS RUN:
- flake8: <pass/fail & top N issues>
- black --check: <pass/fail>
- isort --check: <pass/fail>
- types: <tool + pass/fail>
- tests: <results>
- security: <findings or “none”>

NEXT ACTION:
- If PASS: merge/squash.
- If CHANGES: list ordered steps + minimal diffs.

Confirmation Rules
- Never suggest force-push/history rewrites without explicit approval.
- Migrations/data changes require a tested rollback snippet.
