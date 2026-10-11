# Automated checks

Run `python -m pytest -q` from the repository root. pytest.ini limits discovery to tests/. Checks cover label handling, grouping/leakage, preprocessing, model aggregation, policy boundaries, feedback, inference, metric denominators, controlled edits, session invalidation, artifact identity and evaluation-manifest integrity. The private trained-artifact round-trip skips without checkpoints; historical delivery reports record earlier execution with fitted artifacts.

The CI matrix includes Linux and Windows/Python 3.12. A configured job is not proof of a passing remote run; consult GitHub Actions. scripts/smoke_app.py exercises live upload/comparison APIs and HTTP blocking of a real temporary synthetic private file.
