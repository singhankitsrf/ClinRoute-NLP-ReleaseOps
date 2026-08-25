# Synthetic referral data

No real patient text is included. Generate the 3,000-row demo corpus locally or in CI with:

```bash
python scripts/generate_synthetic_data.py --rows 3000 --seed 42
```

The generated bulk CSV is intentionally ignored by Git.
