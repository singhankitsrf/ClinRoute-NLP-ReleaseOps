# Reproducible evidence

`baseline_metrics.json` is an executed run, not an illustrative score.
`predictions.jsonl` contains class probabilities and reference labels for each held-out task.
`split_manifest.json` contains SHA-256 digests of normalized notes and their partition.
No original medical data are used. Run the commands in `docs/MODEL_CARD.md` to reproduce.

The corpus reduces from 3,000 generated records to 330 unique redacted notes.
The benchmark is an engineering fixture with shared template vocabulary and explicit urgency cues.
It cannot support clinical-performance claims.

The release workflow trains a candidate, checks it against this versioned benchmark, and
passes the **same weights** to container publishing. Invalid or incomparable metrics fail closed.
