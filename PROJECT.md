# ClinRoute NLP ReleaseOps — Project Charter

**Owner:** Ankit Kumar Singh  
**Portfolio role:** Senior NLP / ML Engineer · AI Lead · MLOps Engineer  
**Project type:** NLP release engineering and model-aware CI/CD reference implementation

## Product objective

Demonstrate an NLP system where the model is treated as a governed software dependency: data contracts, redaction, route/urgency inference, confidence policy, reproducible evaluation, regression gates, release provenance, browser/server deployment, and CI/CD are managed together.

## Current delivered scope

- synthetic referral-data generator
- identifier redaction and lightweight entity extraction
- TF-IDF/logistic-regression baseline
- optional Transformer candidate path
- route and urgency prediction
- confidence-based review policy
- model-regression gate
- FastAPI + Docker server path
- CodeQL and GitHub Actions
- browser-exported model with Python/JavaScript parity checks
- live Hugging Face Static Space

## Delivery roadmap

### Phase 1 — Reproducible NLP ReleaseOps — COMPLETE
- [x] deterministic synthetic data generation
- [x] baseline training and evaluation
- [x] data-contract checks
- [x] regression gating
- [x] portable browser inference export
- [x] CI/CD and Hugging Face deployment

### Phase 2 — Stronger evaluation — NEXT
- [ ] Add richer synthetic linguistic variation and adversarial cases
- [ ] Add subgroup/error-slice evaluation
- [ ] Add calibration and selective-review monitoring by route/urgency class
- [ ] Add Transformer candidate benchmark with reproducible provenance
- [ ] Add model-card release comparison across candidates

### Phase 3 — Production-readiness evidence
- [ ] Add authentication/authorization around API serving
- [ ] Add structured telemetry and drift monitoring
- [ ] Add shadow/canary release path
- [ ] Add approved real-world evaluation only when governance permits
- [ ] Publish operational SLOs only after measured deployment

## Success criteria

1. Every release reproduces its benchmark and provenance.
2. Browser and Python inference remain numerically aligned.
3. Model regressions block release automatically.
4. Synthetic benchmark results are never represented as clinical generalization.

## Risks and controls

| Risk | Control |
|---|---|
| Synthetic benchmark overstatement | explicit synthetic-data boundary |
| Model regression | release gate + CI |
| Inference-runtime drift | JavaScript/Python parity validation |
| Low-confidence routing | review-required policy |

## Recruiter signal

NLP · scikit-learn · Transformers · FastAPI · Docker · GitHub Actions · CodeQL · Model Evaluation · CI/CD · Responsible AI
