---
title: ClinRoute NLP
emoji: 🩺
colorFrom: blue
colorTo: indigo
sdk: static
app_file: index.html
pinned: true
license: mit
---

# ClinRoute NLP — Browser ML Demonstration

A recruiter-facing, client-side deployment of the repository's reproducible TF-IDF + logistic-regression referral-routing baseline.

The Space performs inference entirely in the browser from exported, versioned model parameters. It demonstrates identifier redaction, ENT service routing, stated-urgency classification, confidence-based review routing, lightweight entity extraction, and reproducible evaluation evidence.

## Evidence boundary

The benchmark uses synthetic templated referrals only. High synthetic accuracy is expected because templates share vocabulary and urgency is explicitly stated in the generated text. Results are engineering/reproducibility evidence, not clinical validation or evidence of real-world generalization.

Source: https://github.com/singhankitsrf/ClinRoute-NLP-ReleaseOps

Author: Ankit Kumar Singh
