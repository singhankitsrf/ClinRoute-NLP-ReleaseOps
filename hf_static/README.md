---
title: ClinRoute NLP ReleaseOps
emoji: 🩺
colorFrom: blue
colorTo: indigo
sdk: static
app_file: index.html
pinned: true
license: mit
short_description: End-to-end NLP MLOps with CI/CD and browser deployment
tags:
- nlp
- mlops
- healthcare-ai
- scikit-learn
- model-evaluation
- ci-cd
- responsible-ai
- browser-inference
- static
---

# ClinRoute NLP ReleaseOps — End-to-End Deployment Project

**Author:** Ankit Kumar Singh  
**Positioning:** Applied AI • NLP • MLOps • CI/CD • Responsible AI • Healthcare AI • Cloud/Platform Engineering  
**Live runtime:** Hugging Face Static Space  
**Source repository:** https://github.com/singhankitsrf/ClinRoute-NLP-ReleaseOps

ClinRoute is a recruiter-facing **end-to-end NLP deployment and release-engineering project**. It demonstrates how an ML system can move from controlled data generation through preprocessing, training, calibrated evaluation, regression gating, portable inference export, runtime parity validation, and automated deployment.

> **Evidence boundary:** The benchmark uses synthetic templated ENT referrals only. The results below demonstrate reproducibility and engineering controls; they are **not clinical validation** and do not establish real-world generalization.

## What this project demonstrates

- reproducible synthetic-data generation with a fixed random seed
- identifier redaction before model fitting
- normalized-text deduplication before train/test splitting
- zero exact normalized train/test overlap
- two production-style prediction tasks: ENT service routing and stated urgency classification
- TF-IDF + logistic-regression baseline with versioned model artifacts
- accuracy, macro-F1, confusion matrices, expected calibration error (ECE), and multiclass Brier score
- confidence-based `review_required` policy
- lightweight symptom, finding, and duration entity extraction
- model-regression gates in CI/CD
- export of trained scikit-learn vocabulary, IDF weights, coefficients, and intercepts into a portable browser artifact
- JavaScript/scikit-learn probability parity validation before release
- static application smoke testing
- automated Hugging Face publication from GitHub Actions using a repository secret

## End-to-end system flow

```text
Synthetic referral generator
        ↓
Identifier redaction
        ↓
Normalization + deduplication
        ↓
Deterministic stratified train/test split
        ↓
Dual task training
  ├─ ENT route classifier
  └─ urgency classifier
        ↓
Evaluation + calibration metrics
        ↓
Model regression gate
        ↓
Portable model export
(vocabulary + IDF + coefficients + intercepts)
        ↓
Browser/scikit-learn parity test
        ↓
Static bundle smoke test
        ↓
GitHub Actions release pipeline
        ↓
Hugging Face Static Space
        ↓
Interactive recruiter-facing demo
```

## Measured reproducible benchmark

| Evidence | Result |
|---|---:|
| Generated synthetic referrals | 3,000 |
| Unique normalized referrals after deduplication | 330 |
| Training samples | 264 |
| Test samples | 66 |
| Exact normalized train/test overlap | 0 |
| Route accuracy | 1.000 |
| Route macro-F1 | 1.000 |
| Route ECE | ~0.154 |
| Route multiclass Brier score | ~0.030 |
| Urgency accuracy | 1.000 |
| Urgency macro-F1 | 1.000 |
| Urgency ECE | ~0.207 |
| Urgency multiclass Brier score | ~0.067 |

The high synthetic accuracy is expected because the generator uses templated language and urgency is stated explicitly in the text. The project therefore treats these values as **pipeline reproducibility evidence**, not evidence of clinical performance.

## Reproducibility and provenance

The training/evaluation pipeline records and validates:

- fixed seed (`42`)
- dataset SHA-256
- normalized-corpus SHA-256
- train/test split manifest
- prediction evidence
- model artifact hashes
- runtime/library versions
- source Git revision
- portable runtime contract

This makes the release auditable: a recruiter or engineer can trace the live browser deployment back to the validated GitHub source and measured evaluation output.

## Deployment architecture

The public Hugging Face demo uses a **client-side static inference runtime**. The validated Python/scikit-learn model is exported into browser-readable parameters, then the JavaScript implementation reproduces TF-IDF transformation and logistic-regression probability calculations locally.

Before publication, CI compares browser probabilities with Python `predict_proba` using a strict numerical tolerance. The Space is published only after that parity check, the model-regression gate, and application smoke tests pass.

### Runtime privacy boundary

- inference runs in the visitor's browser
- the static application does not require a Python inference server
- application code does not persist entered referral text
- users are instructed to use fictional/synthetic text only
- identifier redaction is best-effort and is not a certified de-identification system

## CI/CD release controls

```text
Git push / PR
   ↓
Install pinned/validated dependencies
   ↓
Reproduce benchmark
   ↓
Run model regression gate
   ↓
Export portable browser model
   ↓
Validate JS ↔ scikit-learn probability parity
   ↓
Smoke-test static application
   ↓
Publish validated bundle to Hugging Face
```

The repository also retains a **Python + FastAPI + Gradio + Docker** server-runtime implementation, demonstrating how the same NLP service can be packaged for a conventional hosted inference environment.

## Engineering decisions

**Why a simple baseline?**  
The live baseline is intentionally interpretable, reproducible, CPU-efficient, and easy to regression-test. A dual-head Transformer training path remains available in the GitHub repository, but the public demo does not imply Transformer-derived performance when the validated runtime is the TF-IDF baseline.

**Why calibration metrics?**  
A routing system should not be evaluated on accuracy alone. ECE and Brier score expose confidence quality and support explicit review-routing policies.

**Why browser deployment?**  
It provides a zero-server-cost, immediately accessible demonstration while preserving a verifiable mapping to the validated scikit-learn model.

## Responsible-use statement

This project is a **software/NLP engineering portfolio demonstration**. It must not be used as a clinical decision-maker without approved real-world datasets, patient-level split controls, external validation, clinical oversight, governance, security review, and relevant regulatory/organizational approval.

## Explore the implementation

- **GitHub source:** https://github.com/singhankitsrf/ClinRoute-NLP-ReleaseOps
- **Evaluation evidence:** https://github.com/singhankitsrf/ClinRoute-NLP-ReleaseOps/tree/main/evaluation
- **Hugging Face Space:** https://huggingface.co/spaces/singhankit491/clinroute-nlp

### Portfolio signal

This project is designed to demonstrate **AI Lead / Senior ML Engineering** capability across model development, reproducibility, calibration, responsible AI, release governance, CI/CD, deployment architecture, and evidence-backed technical communication—not merely a polished user interface.
