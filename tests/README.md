# Automated checks

Run `python -m pytest -q`. There are 30 checks covering label handling, grouping/leakage, preprocessing, aggregation/model dimensions, policy boundaries, feedback, inference, three-state denominators and controlled capture edits. The private trained-artifact round-trip test skips when checkpoints are absent; it passed in the maintainer and fresh environments.
