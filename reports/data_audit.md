# SCIN data audit

## Decision

GO for a small research baseline. Metadata and sample images are accessible, and label handling is explicit. Step 5 must group cases connected by shared image paths, address the missing object, and save leakage-free splits. No split or model has been produced yet.

## Sources and provenance

- Official metadata: https://storage.googleapis.com/dx-scin-public-data/dataset/scin_cases.csv and https://storage.googleapis.com/dx-scin-public-data/dataset/scin_labels.csv
- Schema: https://github.com/google-research-datasets/scin/blob/main/dataset_schema.md
- License: https://github.com/google-research-datasets/scin/blob/main/LICENSE
- Access example: https://github.com/google-research-datasets/scin/blob/main/scin_demo.ipynb
- Paper: Ward A, Li J, Wang J, et al. Creating an Empirical Dermatology Dataset Through Crowdsourcing With Web Search Advertisements. JAMA Network Open. 2024;7(11):e2446615. https://doi.org/10.1001/jamanetworkopen.2024.46615

CSV SHA-256 digests, byte counts, ETags, and reviewed schema/license blob SHAs are in data_audit.json. The audit used the official CSV distribution rather than the Hugging Face conversion. Source CSVs contain release 1.0.0. Raw data and sample images remain outside Git.

## Dataset structure

| Measure | Observed |
| --- | ---: |
| Case rows / unique case IDs | 5,033 |
| Label rows | 5,033 |
| Cases matched to labels | 5,033 |
| Image references | 10,407 |
| Unique referenced image paths | 10,380 |
| Available image objects | 10,379 |
| Missing referenced objects | 1 |
| Shared image-path groups | 15 |
| References within those groups | 42 |

All 15 repeated paths span multiple cases. A case-ID-only split is therefore insufficient: keep all connected cases sharing an image in the same split, or apply a documented duplicate-removal policy. GCS MD5 comparison found no further identical-content groups among distinct available referenced paths; perceptual duplicates were not searched.

## Label semantics and actual encoding

The schema describes the field as a boolean assessment of whether the skin condition can be determined from a case's images. The CSV instead contains categorical tokens. Python truthiness must never be used to parse them.

| Observed token | Binary policy |
| --- | --- |
| DEFAULT_YES_IMAGE_QUALITY_SUFFICIENT | 1: operational gradable label |
| NO_IMAGE_QUALITY_INSUFFICIENT | 0: operational ungradable label |
| YES_IMAGE_QUALITY_SUFFICIENT_NO_DISCERNIBLE_PATHOLOGY | Exclude this vote as semantically ambiguous for the binary task |
| Blank | Missing vote |
| Unknown token | Stop and review; do not silently map |

The mapping is an operational research choice, not proof of pure capture quality. The no-discernible-pathology category is separated because technical image quality and condition gradability are different concepts. Do not infer disease labels or use condition diagnoses as features.

## Reviewer counts and cohort selection

Reviewer 1 has a value for every case. Reviewers 2 and 3 are each missing in 4,317 cases. Counting only the two unambiguous categories, 714 cases have at least two valid votes, 4,262 have one, and 57 have none. Among the multi-valid-vote cases, 346 contain binary disagreement (48.5% of 714).

The established policy requires at least two valid votes and excludes ties:

| Result | Cases |
| --- | ---: |
| Eligible gradable | 557 |
| Eligible ungradable | 153 |
| Ties | 4 |
| Insufficient valid votes | 4,319 |
| Total eligible | 710 |

For comparison only, permitting one valid vote retains 4,972 cases (3,003 gradable, 1,969 ungradable), with 57 insufficient and 4 ties. This alternative is not enabled for training. The strict cohort represents about 14.1% of SCIN and is selected by review availability; report its selection bias and modest size. Consensus is not clinical ground truth. Cohort counts can decrease after step-5 missing-image handling.

## Image checks

Using seed 42, sampled 12 eligible cases balanced across binary labels and decoded all their 35 images. All were readable RGB PNGs. Widths ranged from 594 to 1,080 pixels; heights from 435 to 1,080 pixels. This confirms sample access and loading, not readability of all 10,379 available objects. The one missing object was found by full inventory comparison.

## Missingness and limitations

Full per-field blank/null counts and raw label-category counts are recorded in data_audit.json. Sentinel values such as AGE_UNKNOWN are not counted as blank/null missingness. No subgroup performance claim is made.

No full-dataset decode, perceptual duplicate search, model training, score threshold selection, or evaluation has been performed. Single-image inference still differs from the case-level labels. Keep data, case IDs, image paths, and sample-level audit details local; publish only reviewed aggregates.

## Reproduction

```bash
python scripts/audit_scin.py --sample-cases 12 --seed 42
python -m pytest tests/test_data_loader.py -q
```

The script downloads the two official CSVs, inventories public image objects, and downloads only a deterministic sample. Aggregate results go to reports; raw metadata, object inventory, image checks, and images go to data/raw. The Colab audit notebook can write aggregates to persistent Drive storage.
