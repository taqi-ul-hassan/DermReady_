# Prepared cohort and saved splits

Step 5 completed. The private manifests and CSV split assignments were saved locally; the public repository contains code, aggregate counts, and reproducibility hashes only.

## Eligibility

Strict consensus retains 710 of 5,033 cases, with 557 operational gradable and 153 operational ungradable labels. Require at least two unambiguous votes; exclude ties and insufficient votes. Preserve the raw reviewer tokens, counts, disagreement flag, and exclusion reasons in the case manifest.

Exclude an entire case if any listed image is unavailable, rather than treating a partial image set as the original labeled set. The one incomplete case was already outside the strict cohort, so it does not reduce the 710 eligible cases. Exclusion reasons overlap: 4,319 insufficient-vote cases, 4 ties, and 1 incomplete-image-set case produce 4,323 distinct excluded cases.

## Split counts

| Split | Cases | Gradable | Ungradable | Image references |
| --- | ---: | ---: | ---: | ---: |
| Train | 497 | 390 | 107 | 1,379 |
| Validation | 106 | 83 | 23 | 295 |
| Test | 107 | 84 | 23 | 299 |
| Total | 710 | 557 | 153 | 1,973 |

Seed: 42. Target fractions: 70%/15%/15%. Whole-case/group rounding produces 106 validation and 107 test cases. A deterministic search over 512 group permutations selects the allocation closest to target class counts; it never reads model predictions or image pixels.

## Leakage prevention

Build connected components across ALL cases before filtering, so excluded cases cannot break a duplicate chain. Connect cases by shared image path and equal available-object MD5. All 15 shared-path groups were considered; none connects multiple cases inside this selected cohort, whose eligible components are therefore singletons.

Verification passed with zero cross-split case, component, image-path, or known-content-hash overlap. This does not rule out perceptual duplicates or multiple independent submissions by the same contributor. No identity inference was attempted.

## Private outputs

- data/processed/cases.jsonl: all case records, raw votes, consensus, exclusions, image paths, component IDs, and assignment.
- data/processed/images.csv: one row per image reference, original image index, shot type, availability, object hash, and case assignment. It has no definitive image-level label.
- data/splits/assignments.csv and train.csv, validation.csv, test.csv: eligible case-level assignments and labels.
- data/splits/provenance.json: seed, source hashes, policy, counts, and output hashes.

The same preparation run reproduces byte-identical artifacts. Changed sources, seed, or requested fractions require an explicit --overwrite for an intentional new experiment. Keep the test split fixed after preparation; training uses train, threshold selection uses validation, and final evaluation uses test.

## Reproduction

```bash
python scripts/audit_scin.py --sample-cases 12 --seed 42
python scripts/prepare_scin.py --config configs/experiment.yaml
python -m pytest tests/test_data_loader.py tests/test_splits.py -q
```

See notebooks/02_prepare_data.ipynb to create persistent private manifests/splits in your own Drive. Report JSON includes source and output SHA-256 hashes; compare assignments.csv against the recorded hash to confirm exact reproduction.

## Limits

The two-reviewer cohort is selected and relatively small, particularly the 23 ungradable cases in each holdout. Metrics need uncertainty intervals and cautious interpretation. Object availability is not full image readability; all eligible images will need decode checks during preprocessing. Gradability supervision remains case-level and is not a pure capture-quality label. No training or held-out model evaluation has occurred.
