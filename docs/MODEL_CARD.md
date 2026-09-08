---
language: en
license: mit
library_name: sklearn
pipeline_tag: text-classification
tags:
  - synthetic-data
  - healthcare-nlp
  - portfolio
---
# ClinRoute synthetic baseline

Author: Ankit Kumar Singh.
Two independent TF-IDF/logistic-regression classifiers predict ENT service and stated urgency.
The Gradio demo uses this CPU baseline. It does not claim to run the Transformer candidate.

## Data and evaluation

Generate 3,000 fictional referrals with seed 42. Redact identifiers and normalize text,
then remove duplicates before a stratified 80/20 split. This produces 330 unique notes,
264 training notes and 66 test notes, with zero exact normalized-text overlap.
See `evaluation/baseline_metrics.json`, `predictions.jsonl` and `split_manifest.json`.
The measured run reaches macro-F1 1.0 on both tasks; route ECE is approximately 0.154
and urgency ECE approximately 0.207. These are **synthetic template results**, not clinical accuracy.
Urgency is explicitly stated in the text, and train/test notes share template vocabulary.
High scores do not establish generalization to unseen real referral language.

## Reproduce

```bash
pip install -r hf_space/requirements.txt
PYTHONPATH=.:src python scripts/generate_synthetic_data.py --rows 3000 --seed 42
PYTHONPATH=.:src python training/train_baseline.py --metrics evaluation/candidate_metrics.json
python scripts/model_regression_gate.py --baseline evaluation/baseline_metrics.json --candidate evaluation/candidate_metrics.json
```

## Limits

English synthetic text only. No external clinical evaluation. Entity extraction and redaction
are limited rules, not comprehensive medical NER or certified de-identification.
Confidence is not a safety guarantee. Low-confidence outputs request review.
Not intended for real patient triage, treatment, or autonomous medical decisions.

## Artifacts

Runtime models are built locally or during Docker build and are not committed to GitHub.
The publisher can upload only validated synthetic model weights to Hugging Face.
Joblib artifacts must be loaded only from a trusted source with matching pinned dependencies.
